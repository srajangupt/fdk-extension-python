async def auth(request):
    # Write you code here to return initial launch url
    return request.conn_info.ctx.extension.base_url + "/_healthz"


async def uninstall(request):
    # Write your code here to cleanup data related to extension
    # If task is time taking then process it async on other process
    pass


extension_handler = {
    "auth": auth,
    "uninstall": uninstall
}
