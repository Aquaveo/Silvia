from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import CustomSetting
from tethys_sdk.app_settings import PersistentStoreDatabaseSetting

class Silvia(TethysAppBase):
    """
    Tethys app class for Silvia.
    """

    name = 'Silvia'
    index = 'home'
    icon = 'silvia/images/silvia.png'
    package = 'silvia'
    root_url = 'silvia'
    color = '#2980b9'
    description = 'Sistema de Monitoreo de Movimientos en Masa Potenciales generados por Lluvias Intensas (SILVIA)'
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='silvia',
                controller='silvia.controllers.home'
            ),
            UrlMap(
                name='floods',
                url='floods/',
                controller='silvia.controllers.floodAtributes'
            ),
            UrlMap(
                name='dates',
                url='dates/',
                controller='silvia.controllers.floodDates'
            ),
        )

        return url_maps
    
    def custom_settings(self):
        """
        Example custom_settings method.
        """
        custom_settings = (
            CustomSetting (
                name='flood_info',
                type=CustomSetting.TYPE_STRING,
                description='path/url file containing data about flood information',
                required=True
            ),

        )

        return custom_settings

    def persistent_store_settings(self):
        """
        Add one or more persistent_stores.
        """
        # Create a new persistent store (database)
        stores = (
            PersistentStoreDatabaseSetting(
                name='flooded_addresses',
                initializer='silvia.init_stores.init_flooded_addresses_db',
                spatial=True,
                required=True,
            ),
        )

        return stores