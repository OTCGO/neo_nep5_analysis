/**
 * @api {get} /api/main_net/v1/get_assets
 * @apiName All Asset
 * @apiGroup Asset
 *
 *
 *
{
	"status": "OK",
	"code": 200,
	"data":[
    {
        "type": "type_string",
        "txid": "tx_id_string",
        "precision": integer,
        "owner": "hash_string",
        "name": [
        {
            "name": "name_string",
            "lang": "language_code_string"
        },
        ...
        ],
        "issued": float,
        "amount": float,
        "admin": "hash_string"
    },
    ...
    ] ,
	"server_time": 1496727468000
}
 */
