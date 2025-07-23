import enum
import os
import uuid
import json
from time import sleep
from azure.kusto.data import KustoConnectionStringBuilder, ClientRequestProperties, KustoClient, DataFormat
from azure.kusto.data.exceptions import KustoClientError, KustoServiceError
from azure.kusto.ingest import IngestionProperties, BaseIngestClient, QueuedIngestClient, FileDescriptor, BlobDescriptor

class AuthenticationModeOptions(enum.Enum):
    """
    AuthenticationModeOptions - represents the different options to autenticate to the system
    """

    UserPrompt = ("UserPrompt",)
    ManagedIdentity = ("ManagedIdentity",)
    AppKey = ("AppKey",)
    AppCertificate = "AppCertificate"

class Utils:
    class Authentication:
        """
        Authentication module of Utils - in charge of authenticating the user with the system
        """

        @classmethod
        def generate_connection_string(cls, cluster_url: str, authentication_mode: AuthenticationModeOptions) -> KustoConnectionStringBuilder:
            """
            Generates Kusto Connection String based on given Authentication Mode.
            :param cluster_url: Cluster to connect to.
            :param authentication_mode: User Authentication Mode, Options: (UserPrompt|ManagedIdentity|AppKey|AppCertificate)
            :return: A connection string to be used when creating a Client
            """
            # Learn More: For additional information on how to authorize users and apps in Kusto,
            # see: https://docs.microsoft.com/azure/data-explorer/manage-database-permissions

            if authentication_mode == AuthenticationModeOptions.UserPrompt.name:
                # Prompt user for credentials
                return KustoConnectionStringBuilder.with_interactive_login(cluster_url)

            elif authentication_mode == AuthenticationModeOptions.ManagedIdentity.name:
                # Authenticate using a System-Assigned managed identity provided to an azure service, or using a User-Assigned managed identity.
                # For more information, see https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview
                return cls.create_managed_identity_connection_string(cluster_url)

            elif authentication_mode == AuthenticationModeOptions.AppKey.name:
                # Learn More: For information about how to procure an AAD Application,
                # see: https://docs.microsoft.com/azure/data-explorer/provision-azure-ad-app
                # TODO (config - optional): App ID & tenant, and App Key to authenticate with
                return KustoConnectionStringBuilder.with_aad_application_key_authentication(
                    cluster_url, os.environ.get("APP_ID"), os.environ.get("APP_KEY"), os.environ.get("APP_TENANT")
                )

            elif authentication_mode == AuthenticationModeOptions.AppCertificate.name:
                return cls.create_application_certificate_connection_string(cluster_url)

            else:
                Utils.error_handler(f"Authentication mode '{authentication_mode}' is not supported")

        @classmethod
        def create_managed_identity_connection_string(cls, cluster_url: str) -> KustoConnectionStringBuilder:
            """
            Generates Kusto Connection String based on 'ManagedIdentity' Authentication Mode.
            :param cluster_url: Url of cluster to connect to
            :return: ManagedIdentity Kusto Connection String
            """

            return (
                KustoConnectionStringBuilder.with_aad_managed_service_identity_authentication(cluster_url)
            )

        @classmethod
        def create_application_certificate_connection_string(cls, cluster_url: str) -> KustoConnectionStringBuilder:
            """
            Generates Kusto Connection String based on 'AppCertificate' Authentication Mode.
            :param cluster_url: Url of cluster to connect to
            :return: AppCertificate Kusto Connection String
            """

            # TODO (config - optional): App ID & tenant, path to public certificate and path to private certificate pem file to authenticate with
            app_id = os.environ.get("APP_ID")
            app_tenant = os.environ.get("APP_TENANT")
            private_key_pem_file_path = os.environ.get("PRIVATE_KEY_PEM_FILE_PATH")
            cert_thumbprint = os.environ.get("CERT_THUMBPRINT")
            public_cert_file_path = os.environ.get("PUBLIC_CERT_FILE_PATH")  # Only used for "Subject Name and Issuer" auth
            public_certificate = None
            pem_certificate = None

            try:
                with open(private_key_pem_file_path, "r") as pem_file:
                    pem_certificate = pem_file.read()
            except Exception as ex:
                Utils.error_handler(f"Failed to load PEM file from {private_key_pem_file_path}", ex)

            if public_cert_file_path:
                try:
                    with open(public_cert_file_path, "r") as cert_file:
                        public_certificate = cert_file.read()
                except Exception as ex:
                    Utils.error_handler(f"Failed to load public certificate file from {public_cert_file_path}", ex)

                return KustoConnectionStringBuilder.with_aad_application_certificate_sni_authentication(
                    cluster_url, app_id, pem_certificate, public_certificate, cert_thumbprint, app_tenant
                )
            else:
                return KustoConnectionStringBuilder.with_aad_application_certificate_authentication(
                    cluster_url, app_id, pem_certificate, cert_thumbprint, app_tenant
                )

    @classmethod
    def load_configs(cls, config_file_name: str) -> dict :
        """
        Loads JSON configuration file, and sets the metadata in place.
        :param config_file_name: Configuration file path.
        """
        try:
            with open(config_file_name, "r") as config_file:
                return json.load(config_file)
        except Exception as ex:
            Utils.error_handler(f"Couldn't read load config file from file '{config_file_name}'", ex)

    @staticmethod
    def error_handler(error: str, e: Exception = None) -> None:
        """
        Error handling function. Will mention the appropriate error message (and the exception itself if exists), and will quit the program.
        :param error: Appropriate error message received from calling function
        :param e: Thrown exception
        """
        print(f"Script failed with error: {error}")
        if e:
            print(f"Exception: {e}")
