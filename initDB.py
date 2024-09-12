from deta import Deta  # Import Deta

# Initialize with a Project Key
deta = Deta("a0zwczne_HrmswE9qPZscFqZsQVxZVxxZQoC8UwVj")

# This how to connect to or create a database.
db = deta.Base("hanna_images")



# db_profile.put({"email":"hanna@gm.com", "hashed_password":"323f02" }, "one")
db.put({
      "order": 160,
      "slug": "products",
      "file": "DSC05077.jpg",
      "description": ""
         })
