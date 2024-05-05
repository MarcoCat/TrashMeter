from app import app

if __name__ == '__main__':
    from app import create_database
    create_database(app)
    app.run(debug=True)
