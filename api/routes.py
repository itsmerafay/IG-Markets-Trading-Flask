from flask import Flask ,request, jsonify, json, Blueprint
import requests
from .credentials import *
api_blueprint = Blueprint('api_blueprint', __name__)

@api_blueprint.route('/market/navigation', methods = ["GET"])
def get_market_navigation():
    url = 'https://api.ig.com/gateway/deal/marketnavigation'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # filtered_nodes = [node for node in data.get("nodes",[]) if any(keyword in node["name"] for keyword in ["Shares", "Options", "Future"])]
        # markets = data.get('markets')
        # if markets is None:
        #     filtered_markets = []
        # else:
        #     filtered_markets = [market for market in markets if any(keyword in market.get('instrumentName', '') for keyword in ['Shares', 'Options', 'Future'])]

        return jsonify({
                "status":True,
                "data":data                
            })

    else:
        print(f"HTTP Error: {response.status_code}")
        return jsonify({
            "status":False,
            "error":response.status_code
        })



# @api_blueprint.route('/find_market', methods=['POST'])
# def find_market_with_user_input():
#     request_data = request.json
#     node_ids = request_data.get('node_ids', [])

#     # for instance : if nodeids are not the type of lists
#     if not node_ids or not isinstance(node_ids, list):
#         return jsonify({
#             "status": False,
#             "error": "A list of node IDs is required."
#         }), 400

#     # Function to get market navigation with node_id
#     def get_markets_navigation_with_nodeid(node_id):
#         url = f'https://api.ig.com/gateway/deal/marketnavigation/{node_id}'
#         response = requests.get(url, headers=headers)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             print(f"HTTP Error: {response.status_code}")
#             return None

#     results = []

#     # Iterate over node IDs
#     for node_id in node_ids:
#         data = get_markets_navigation_with_nodeid(node_id)
        
#         if data is None:
#             results.append({
#                 "node_id": node_id,
#                 "status": False,
#                 "error": f"Failed to retrieve data for node ID: {node_id}"
#             })
#             continue
        
#         # Usually the last one.
#         if data.get('markets'): 
#             results.append({
#                 "node_id": node_id,
#                 "status": True,
#                 "markets": data['markets']
#             })
        
#         # we have done data['nodes'] as the orig api has nodes named in it.
#         elif data.get('nodes'):
#             results.append({
#                 "node_id": node_id,
#                 "status": True,
#                 "available_nodes": [
#                     {
#                     "id": node['id'],
#                     "name": node['name']
#                     } 
#                     for node in data['nodes']
#                     ]
#             })
#         else:
#             results.append({
#                 "node_id": node_id,
#                 "status": False,
#                 "error": "No further nodes or markets available."
#             })

#     return jsonify(results)



@api_blueprint.route('/find_market', methods=["POST"])
def find_market():
    request_data = request.json
    node_ids = request_data.get("node_ids",[])

    if not node_ids or not isinstance(node_ids, list):
        return jsonify({
            "status":False,
            "error":"Node ids are required for market search"
        }), 400
    
    def get_markets_navigation_with_nodeid(node_id):
        url = f'https://api.ig.com/gateway/deal/marketnavigation/{node_id}'
        response = requests.get(url, headers=headers)
        if response.status_code == 200 :
            return response.json()
        else:
            return jsonify({
                "status":False,
                "error": f"Http Error : {response.status_code}"
            })
    
    results = []
        
    for node_id in node_ids:
        data = get_markets_navigation_with_nodeid(node_id)

        if data is None:
            results.append({
                "node_id":node_id,
                "status":False,
                "error": f"Data not found for the node id {node_id}"
            })
        
        if data.get("markets"):
            results.append({
                "node_id":node_id,
                "status":True,
                "markets":data["markets"]
            })

        elif data.get("nodes"):
            # results.append({
            #     "node_id":node_id,
            #     "status":True,
            #     "available_nodes":[{
            #         "id": node["id"],
            #         "name": node["name"]

            #     }for node in data["nodes"]]
            # })
            pass
        else:
            results.append({
                "node_id": node_id,
                "status": False,
                "error": "No furtther noeds available"
            })
    return jsonify(results)


@api_blueprint.route('/watchlist', methods=["GET"])
def get_watchlist():
    url = 'https://api.ig.com/gateway/deal/watchlists'
    response = requests.get(url, headers=headers)
    data = response.json()
    if response.status_code == 200:
        return jsonify({
            "status":True,
            "data":data

        }), 200
    else:
        return jsonify({
            "status": False,
            "error": "Error in getting the watchlist"     
        }), response.status_code
    


@api_blueprint.route('/watchlist', methods=["POST"])
def create_watchlist():
    request_data = request.json
    name = request_data.get("name")
    epics = request_data.get("epics",[])
    url = 'https://api.ig.com/gateway/deal/watchlists'
    payload = {
        "name":name,
        "epics":epics
    }
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    if response.status_code == 200:
        return jsonify({
            "status":True,
            "data":data

        }), 200
    else:
        return jsonify({
            "status": False,
            "error": "Failed to add epics to watchlsits"     
        }), response.status_code



@api_blueprint.route('/watchlist/<watchlist_id>', methods=["DELETE"])
def delete_watchlist(watchlist_id):
    # Verify the watchlist exists before attempting to delete
    get_url = f'https://api.ig.com/gateway/deal/watchlists/{watchlist_id}'
    get_response = requests.get(get_url, headers=headers)
    
    if get_response.status_code != 200:
        return jsonify({
            "status": False,
            "error": f"Watchlist with id {watchlist_id} does not exist.",
            "details": get_response.json() if get_response.content else get_response.text
        }), get_response.status_code
    
    # Attempt to delete the watchlist
    delete_url = f'https://api.ig.com/gateway/deal/watchlists/{watchlist_id}'
    delete_response = requests.delete(delete_url, headers=headers)
    
    if delete_response.status_code == 200:
        return jsonify({
            "status": True,
            "data": f"Successfully deleted the watchlist with id {watchlist_id}"
        }), 200
    else:
        error_details = delete_response.json() if delete_response.content else delete_response.text
        return jsonify({
            "status": False,
            "error": f"Failed to delete watchlist with id {watchlist_id}",
            "details": error_details
        }), delete_response.status_code

