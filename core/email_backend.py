import ssl
import certifi
import smtplib
from django.core.mail.backends.smtp import EmailBackend

class SMTPSSLIgnoreCertBackend(EmailBackend):
    """
    Backend SMTP sobre SSL que ignora la verificación de certificado.
    Útil en entornos donde la CA local no está bien configurada.
    """
    def open(self):
        if self.connection:
            return self.connection

        # 1) Creamos un contexto que NO verifica hostname ni certificado
        context = ssl.create_default_context(cafile=certifi.where())
        context.check_hostname = False
        context.verify_mode   = ssl.CERT_NONE

        # 2) Abrimos una conexión SMTP_SSL (puerto 465) con nuestro contexto
        if self.timeout is not None:
            # Convertimos timeout a float
            timeout = float(self.timeout)
            self.connection = smtplib.SMTP_SSL(
                host=self.host,
                port=self.port,
                timeout=timeout,
                context=context
            )
        else:
            # Sin timeout especificado
            self.connection = smtplib.SMTP_SSL(
                host=self.host,
                port=self.port,
                context=context
            )

        # 3) Login si necesitamos
        if self.username and self.password:
            self.connection.login(self.username, self.password)

        return self.connection
