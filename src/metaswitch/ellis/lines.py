import logging
log = logging.getLogger("metaswitch.ellis.lines")

def derive_impi_from_impu(impu):
    if impu[:4] == "sip:":
        return impu[4:]
    else:
        return None

def get_user_part(impu):
    if impu[:4] == "sip:" or impu[:4] == "tel:":
        impu = impu[4:]
    at_loc = impu.rfind("@")
    return impu[:at_loc]


class Line:
    def __init__(self, owner, impu, impi):
        self.deletion_begun = False
        self.impu = impu
        self.impi = impi
        self.sp_uri = None
        self.irs_uri = None

    def create_elsewhere(self, homestead):
        log.info("Trying to create line {} at Homestead".format(self.impu))
        self.sp_uri = homestead.create_sp(self.irs_uri)
        if self.sp_uri is None:
            log.info("Failed to create service profile")
            self.deletion_begun = True
            return False
        log.info("Created service profile with URL {}".format(self.sp_uri))

        homestead_impu_created_ok = homestead.create_impu(self, self.impu, self.sp_uri)
        if not homestead_impu_created_ok:
            log.info("Failed to create IMPU at Homestead")
            self.deletion_begun = True
            return False
        log.info("Created IMPU at Homestead")

        #simservs_created_ok = homer.create_simservs(self, self.impu, self.simservs)
        #if not simservs_created_ok:
        #    self.deletion_begun = True
        #    return False

        return True

    def to_json(self):
        up = get_user_part(self.impu)
        info = {"formatted_number": up,
         "number": up,
         "sip_username": up,
         "private_id": self.impi,
         "pstn": False,
         "gab_listed": False,
         "sip_uri": self.impu}
        return info

    def try_delete(self, homestead):
        self.deletion_begun = True
        if self.secondary_impu_of is None:
            success = homestead.delete_irs()
            if not success:
                return False
            # Delete the IMPI, bail out on failure
            pass
        # Delete the IMPU, bail out on failure
        # Delete the service profile, bail out on failure
        # Delete the simservs, bail out on failure
        return True

class PrimaryLine(Line):
    def __init__(self, owner, impu):
        self.subsidiary_lines = 0
        impi = derive_impi_from_impu(impu)
        super().__init__(owner, impu, impi)

    def create_elsewhere(self, homestead):
        self.irs_uri = homestead.create_irs()
        if self.irs_uri is None:
            log.info("Failed to create implicit registration set")
            self.deletion_begun = True
            return False
        log.info("Created implicit registration set with URL {}".format(self.irs_uri))

        homestead_impi_created_ok = homestead.create_impi(self, self.impi, self.irs_uri)
        if not homestead_impi_created_ok:
            log.info("Failed to create IMPI at Homestead")
            self.deletion_begun = True
            return False

        log.info("Created IMPI at Homestead")

        return super().create_elsewhere(homestead)

    def clone(self, new_impu):
        new_line = Line(self.owner, new_impu, self.impi)
        successful_creation = new_line.create_elsewhere(self.irs, self.impi)
        if successful_creation:
            self.subsidiary_lines += 1
            return new_line
        else:
            return None

class SecondaryLine(Line):
    def __init__(self, owner, impu, impi, existing_irs_uri):
        self.deletion_begun = False
        self.irs_uri = existing_irs_uri
        super().__init__(self, owner, impu, impi)

