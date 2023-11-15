# FastAPI Shop

## Overview

FastAPI Shop is your go-to starting point for building a modern, efficient, and highly customizable online shop. This
project, powered by **FastAPI**, **SQLAlchemy**, and **Pydantic**, provides a solid foundation for launching or
enhancing your venture with a feature-rich online shopping experience.

## Features

- **RESTful API:** Utilizes FastAPI to deliver a RESTful API for managing products, orders, users, and more.

- **Database Integration:** Integrates SQLAlchemy for database operations, supporting various systems like PostgreSQL,
  MySQL, SQLite, or others.

- **Data Validation:** Leverages Pydantic for request and response data validation, ensuring data integrity and
  security.

- **Authentication and Authorization:** Implements user authentication and authorization mechanisms to secure the
  application.

- **Product Management:** Facilitates the management of products, including adding, updating, and deleting.

- **Order Management:** Supports order creation, tracking, and management.

- **User Management:** Provides user registration, login, and profile management functionalities.

- **Customization:** Easily tailor the project to fit your specific eCommerce requirements and branding.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- [pip](https://pip.pypa.io/en/stable/)
- [Virtualenv](https://pypi.org/project/virtualenv/) (optional but recommended)

### Installation

1. **Clone the repository:**

    ```shell
    git clone https://github.com/zamaniamin/fastapi-shop.git
    ```

2. **Navigate to the project directory:**

    ```shell
    cd fastapi-shop
    ```

3. **Create and activate a virtual environment (recommended):**

    ```shell
    virtualenv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4. **Install project dependencies:**

    ```shell
    pip install -r requirements.txt
    ```

### Configuration

To configure your FastAPI Shop project, create a `.env` file by copying the `.env.template` file and filling in the
actual values. Here's an example:

1. Copy `.env.template` to `.env`.
2. Open `.env` in a text editor.
3. Replace the placeholder values with your actual configuration details.
4. Save the file.

### Usage

1. **Start the FastAPI server:**

    ```shell
    uvicorn apps.main:app --reload
    ```

2. **Access the API documentation at** `http://localhost:8000/docs` **to explore and interact with the API endpoints
   using the Swagger UI.**

3. **Add Demo Data:**

    - **Step 1 (Optional):** You can skip this step if you don't want to add your own demo images. The project includes
      existing demo images located at `apps/demo/media/products/{product_id}`.

    - **Step 2:** To prevent conflicts during development, remove your database tables. For development, I recommend
      using SQLite.

    - **Step 3:** Run the following command to create demo data, including fake products with images, a fake admin, and
      a fake user:

    ```bash
    python demo.py
    ```

   This will populate your database with a variety of demo data for testing and development purposes.

## Customization

FastAPI Shop is designed to be highly customizable to suit your eCommerce needs. You can extend and modify the project
by:

- Adding new API endpoints to handle additional features.
- Customizing the database models in `models.py` to reflect your product catalog, user profiles, and more.
- Enhancing the user interface by integrating a front-end framework of your choice.

## Deployment

For deployment, consider using popular cloud platforms like AWS, Google Cloud, or Heroku. Ensure you set up proper
security measures and scalability options.

## Contributing

Contributions to this project are welcome. Feel free to submit bug reports, feature requests, or pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)

## Contact

For questions or inquiries, please contact [Amin Zamani](mailto:aminzamani.work@gmail.com).

---
