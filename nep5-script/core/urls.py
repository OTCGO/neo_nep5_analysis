# coding:utf8
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from .views import (
    BankBindViewSet,
    ANCClaimViewSet,
    ANCClaimSignViewSet,
    OTCAskOrderViewSet,
    OTCBidOrderViewSet,
    FreeAskOrderViewSet,
    FreeBidOrderViewSet,
    OTCSignViewSet,
    ICOAskOrderViewSet,
    ICOBidOrderViewSet,
    ICOSignViewSet,
    ICOViewSet,
    ICOOrderListViewSet,
    ICOCheckPasswordViewSet,
    MarketViewSet,
    BalanceViewSet,
    OrderBookViewSet,
    OrderListViewSet,
    NonceViewSet,
    SignViewSet,
    OrderCancelViewSet,
    TransferViewSet,
    UIDViewSet,
    RedeemListViewSet,
    RedeemCreateViewSet,
    RedeemSignatureViewSet,
    TransferHistoryViewSet,
    BlockCountViewSet,
    HistoryListViewSet,
    BankQueryViewSet
)

schema_view = get_schema_view(
    title='OTCGO.CN API v1',
    renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer]
)

router = routers.DefaultRouter()
router.register(r'v1/claim', ANCClaimViewSet, base_name='api')
router.register(r'v1/claim/sign', ANCClaimSignViewSet, base_name='api')

router.register(r'v1/otc/ask', OTCAskOrderViewSet, base_name='api')
router.register(r'v1/otc/bid', OTCBidOrderViewSet, base_name='api')
router.register(r'v1/otc/free/ask', FreeAskOrderViewSet, base_name='api')
router.register(r'v1/otc/free/bid', FreeBidOrderViewSet, base_name='api')
router.register(r'v1/otc/sign', OTCSignViewSet, base_name='api')

router.register(r'v1/ico/ask', ICOBidOrderViewSet, base_name='api')
router.register(r'v1/ico/bid', ICOAskOrderViewSet, base_name='api')
router.register(r'v1/ico/sign', ICOSignViewSet, base_name='api')
router.register(r'v1/ico', ICOViewSet, base_name='api')
router.register( r'v1/ico/order/(?P<address>\w{34})', ICOOrderListViewSet, base_name='api')

router.register(r'v1/markets', MarketViewSet, base_name='api')
router.register(r'v1/balances/transfer/history/(?P<address>\w{34})', TransferHistoryViewSet, base_name='api')
router.register(r'v1/balances/transfer', TransferViewSet, base_name='api')
router.register(r'v1/balances', BalanceViewSet, base_name='api')
router.register(r'v1/order_book', OrderBookViewSet, base_name='api')
router.register(r'v1/order/(?P<address>\w{34})', OrderListViewSet, base_name='api')
router.register(r'v1/cancel', OrderCancelViewSet, base_name='api')
router.register(r'v1/nonce', NonceViewSet, base_name='api')
router.register(r'v1/sign', SignViewSet, base_name='api')
router.register(r'v1/uid/(?P<address>\w{34})', UIDViewSet, base_name='api')
router.register(r'v1/redeem/(?P<address>\w{34})', RedeemListViewSet, base_name='api')
router.register(r'v1/redeem', RedeemCreateViewSet, base_name='api')
router.register(r'v1/signature/redeem',RedeemSignatureViewSet, base_name='api')
router.register(r'v1/block/count', BlockCountViewSet, base_name='api')
router.register(r'v1/history/(?P<marketId>\w{6})', HistoryListViewSet, base_name='api')

# pay


"bind"
router.register(r'v1/pay/bind', BankBindViewSet, base_name='api')
"query bind query"
router.register(r'v1/pay/info', BankQueryViewSet, base_name='api')


urlpatterns = [
    url(r'^v1/$', schema_view, name='api'),
]

urlpatterns += router.urls
