from app import create_app
from create_flag import create_flag
import os

app = create_app()

def main():
    create_flag(os.getenv("FLAG", "ctf{test_falg}"))
    app.run(debug=True, host='0.0.0.0', port=80)

if __name__ == '__main__':
    main()
