from django.urls import path
from interface.views.server import (
    ServerListView,
    ServerDetailView,
    ServerServiceListView,
)
from interface.views.service import (
    ServiceListView,
    ServiceDetailView
)
from interface.views.proxy import (
    ProxyListView,
    ProxyDetailView
)
from interface.views.proxy_ctl import (
    ProxyServiceCtlView
)
from interface.views.index import index_view

urlpatterns = [

    # 服务器
    path('servers/', ServerListView.as_view()),
    path('server/<int:pk>', ServerDetailView.as_view()),
    path('server/services/', ServerServiceListView.as_view()),

    # 服务
    path("services/", ServiceListView.as_view()),
    path("service/<int:pk>", ServiceDetailView.as_view()),

    # 代理
    path("proxys/", ProxyListView.as_view()),
    path("proxy/<int:pk>", ProxyDetailView.as_view()),

    path("proxy/service/<int:pk>", ProxyServiceCtlView.as_view()),
]
