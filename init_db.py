from bot.db import Base, engine
from bot.models import Complaint

print("🔄 Создание таблиц в базе данных...")
Base.metadata.create_all(bind=engine)
print("✅ Готово!")

# from bot.db import Base, engine
# from bot.models import Complaint
#
# def init():
#     print("🔄 Creating tables if not exist...")
#     Base.metadata.create_all(bind=engine)
#     print("✅ Tables created.")
#
# if __name__ == "__main__":
#     init()
