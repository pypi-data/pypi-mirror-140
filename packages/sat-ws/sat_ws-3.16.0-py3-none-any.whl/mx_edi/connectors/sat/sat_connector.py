import logging
from typing import Dict

from requests import Response

from . import templates, utils
from .certificate_handler import CertificateHandler
from .envelope_signer import EnvelopeSigner
from .sat_login_handler import SATLoginHandler

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class SATConnector:
    """Class to make a connection to the SAT"""

    login_handler: SATLoginHandler
    envelope_signer: EnvelopeSigner
    rfc: str

    def __init__(self, cert: bytes, key: bytes, password: bytes) -> None:
        """Loads the certificate, key file and password to stablish the connection to the SAT

        Creates a object to manage the SAT connection.

        Args:
            cert (bytes): DER Certificate in raw binary
            key (bytes): DER Key Certificate in raw binary
            password (bytes): Key password in binary
        """
        certificate_handler = CertificateHandler(cert, key, password)
        self.rfc = certificate_handler.unique_identifier
        self.login_handler = SATLoginHandler(certificate_handler)
        self.envelope_signer = EnvelopeSigner(certificate_handler)
        _logger.info("Data correctly loaded")

    def send_query(self, data: Dict[str, str]) -> Response:
        data["rfc"] = self.rfc
        envelope = self.envelope_signer.create_common_envelope(
            templates.SolicitaDescarga,
            data,
        )
        return utils.consume(
            "http://DescargaMasivaTerceros.sat.gob.mx/ISolicitaDescargaService/SolicitaDescarga",
            "https://cfdidescargamasivasolicitud.clouda.sat.gob.mx/SolicitaDescargaService.svc",
            envelope,
            token=self.login_handler.token,
        )

    def verify_query(self, data: Dict[str, str]) -> Response:
        data["rfc"] = self.rfc
        envelope = self.envelope_signer.create_common_envelope(
            templates.VerificaSolicitudDescarga,
            data,
        )
        return utils.consume(
            "http://DescargaMasivaTerceros.sat.gob.mx/IVerificaSolicitudDescargaService/VerificaSolicitudDescarga",
            "https://cfdidescargamasivasolicitud.clouda.sat.gob.mx/VerificaSolicitudDescargaService.svc",
            envelope,
            token=self.login_handler.token,
        )

    def download_package(self, data: Dict[str, str]) -> Response:
        """Get the binary response for a package"""
        data["rfc"] = self.rfc
        envelope = self.envelope_signer.create_common_envelope(
            templates.PeticionDescargaMasivaTercerosEntrada,
            data,
        )
        return utils.consume(
            "http://DescargaMasivaTerceros.sat.gob.mx/IDescargaMasivaTercerosService/Descargar",
            "https://cfdidescargamasiva.clouda.sat.gob.mx/DescargaMasivaService.svc",
            envelope,
            token=self.login_handler.token,
        )
