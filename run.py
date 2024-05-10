from app import app

if __name__ == '__main__':
    from app import create_database, reset_database
    reset_database(app)
    app.run(debug=True)