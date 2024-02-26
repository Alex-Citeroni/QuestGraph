from app import app

# Start the Flask application on port 5002 and make it accessible from any IP address
if __name__ == "__main__":
    app.run(port=5002, host="0.0.0.0")
