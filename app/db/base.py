# Import Base từ session
from app.db.session import Base 

# Import tất cả các Model đã viết để Alembic có thể "nhìn thấy" chúng
from app.models.user import User # noqa
from app.models.associations import program_categories # noqa
from app.models.category import Category
from app.models.program import Program # noqa
from app.models.option_group import OptionGroup # noqa
from app.models.option import Option # noqa
from app.models.example import Example # noqa
from app.models.man_page import ManPage # noqa
from app.models.history import History # noqa 
from app.models.favorite import Favorite # noqa

# Lưu ý: Việc import các model ở đây giúp Base.metadata chứa đầy đủ thông tin  về cấu trúc các bảng trong database.