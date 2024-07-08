import io
import json
import base64

from fdk import response


def handler(ctx, data: io.BytesIO=None):
    print("Entering Python Hello World handler", flush=True)
    name = "World"
    try:
        # Read the incoming base64 encoded data
        base64_encoded_data = data.getvalue()
        
        # Decode the base64 data
        decoded_data = base64.b64decode(base64_encoded_data)
        
        # Parse the JSON data
        body = json.loads(decoded_data)
        
        # Extract the 'name' field from the JSON data
        name = body.get("name")
    except (Exception, ValueError) as ex:
        print(f"Error: {str(ex)}", flush=True)

    print(f"Value of name = {name}", flush=True)
    print("Exiting Python Hello World handler", flush=True)
    
    return response.Response(
        ctx, 
        response_data=json.dumps({"message": f"Hello {name}"}),
        headers={"Content-Type": "application/json"}
    )
