from app import create_app

app = create_app()

print("Using database file at:", app.config['SQLALCHEMY_DATABASE_URI'])  # ← Add here

if __name__ == '__main__':
    app.run(debug=True)
