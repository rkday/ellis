import requests

def NoneOnRequestException(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.exceptions.RequestException:
            return None
    return inner

def FalseOnRequestException(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.exceptions.RequestException:
            return False
    return inner

class HomesteadClient:
    def __init__(self, hostname, port=8889):
        self.hostname = hostname
        self.port = str(port)

    @NoneOnRequestException
    def create_irs(self):
        resp = requests.post(self._new_irs_uri())
        if resp.status_code != 201:
            return None
        return resp.headers['Location']

    @FalseOnRequestException
    def delete_irs(self, irs_loc):
        resp = requests.delete(self._irs_uri(irs_loc))
        if (resp.status_code != 200) and (resp.status_code != 201):
            return False
        return True

    @FalseOnRequestException
    def create_impi(self, impi, irs_loc):
        resp = requests.post(self._impi_uri(impi))
        if (resp.status_code != 200) and (resp.status_code != 201):
            return False

        resp = requests.put(self._associate_irs_and_impi_uri(impi, irs_loc))
        if (resp.status_code != 200) and (resp.status_code != 201):
            return False

        return True

    @FalseOnRequestException
    def delete_impi(self, impi, irs_loc):
        resp = requests.delete(self._associate_irs_and_impi_uri(impi, irs_loc))
        if (resp.status_code != 200) and (resp.status_code != 201):
            return False

        resp = requests.delete(self._impi_uri(impi))
        if (resp.status_code != 200) and (resp.status_code != 201):
            return False

        return True

    @NoneOnRequestException
    def create_sp(self, irs_loc):
        resp = requests.post(self._new_sp_uri(irs_loc))
        if resp.status_code != 201:
            return None
        return resp.headers['Location']

    @FalseOnRequestException
    def delete_sp(self, sp_loc):
        resp = requests.delete(self._sp_uri(sp_loc))
        if (resp.status_code != 200) and (resp.status_code != 201):
            return False
        return True

    @FalseOnRequestException
    def create_impu(self, impu, sp_loc):
        resp = requests.post(self._impu_uri(sp_loc, impu))
        if resp.status_code != 201:
            return False
        return True

    @FalseOnRequestException
    def delete_impu(self, impu, sp_loc):
        resp = requests.delete(self._impu_uri(sp_loc, impu))
        if resp.status_code != 201:
            return False
        return True

    def _new_irs_uri(self):
        return self._url("/irs")

    def _irs_uri(self, irs_loc):
        return self._url(irs_loc)

    def _new_sp_uri(self, irs_loc):
        return self._url("{}/service-profiles", irs_loc)

    def _sp_uri(self, sp_loc):
        return self._url(sp_loc)

    def _ifc_uri(self, sp_loc):
        return self._url("{}/filter_criteria", sp_loc)

    def _impu_uri(self, sp_loc, impu):
        return self._url("{}/public_ids/{}", sp_loc, impu)

    def _impi_uri(self, impi):
        return self._url("/private/{}", impi)

    def _associate_irs_and_impi_uri(self, irs_loc, impi):
        return self._url("{}/private_ids/{}", irs_loc, impi)

    def _url(self, path, *args):
        return "http://{}:{}{}".format(self.hostname, self.port, path).format(*args)