from app import app

if __name__ == "__main__":
    # Produktionsmodus verwenden
    app.run(debug=False, host='0.0.0.0', port=5000)
