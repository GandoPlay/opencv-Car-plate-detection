import sqlite3


class DBCars:
    def __init__(self):
        """
        Creates a new table in the CarsDb unless it's already been created.
        """
        self.name = 'CarsDB.db'
        self.data_base = sqlite3.connect(self.name)
        self.cursor = self.data_base.cursor()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Cars(
                       number_plate text,
                       Country text,
                       image blob
                       )""")

        self.close_the_data_base()

    def show(self, country):
        """
        shows all the cars of a certain country
        :param country: the country of the cars we want to see.
        :return: the data of every image in the country: car's number, car's country, car's image in "byte String", car's oid.
        """
        self.connect_to_data_base()

        self.cursor.execute(f"SELECT *, oid FROM Cars WHERE Country ='{country}'")
        data = self.cursor.fetchall()  # extract the data.
        self.close_the_data_base()
        return data

    def DB_TO_STR(self, data):
        txt = '\n'.join(['\n'.join([str(x) for x in t]) for t in data])
        return txt

    def insert(self, num_plate, country, img):
        """
        Insert a new Car to the DataBase.
        :param num_plate: the num Plate of the car.
        :param country: the country of the car.
        :param img: The image of the car.
        :return:
        """
        self.connect_to_data_base()

        self.cursor.execute("INSERT INTO Cars VALUES (:num_plate, :country, :img)",
                            {
                                'num_plate': num_plate,
                                'country': country,
                                'img': img
                            })

        self.close_the_data_base()

    def update(self, num_plate, country, rec_id):
        """
        update an existing car in the dataBase
        :param num_plate: the num Plate of the car
        :param country: the country of the car
        :param rec_id: the oid of the car.
        :return:
        """
        self.connect_to_data_base()

        self.cursor.execute("""UPDATE Cars SET
                    number_plate = :number_plate,
                    country = :country
                    WHERE oid = :oid""",
                            {
                                'number_plate': num_plate,
                                'country': country,
                                'oid': rec_id

                            })

        self.close_the_data_base()

    def delete(self, rec_id):
        """
        this function deletes a car from the DataBase.
        :param rec_id: the oid of the car we want to remove.
        :return:
        """
        self.connect_to_data_base()
        self.cursor.execute(f"DELETE from Cars WHERE oid={rec_id}")
        self.close_the_data_base()

    def connect_to_data_base(self):
        """
        Connect to the dataBase
        :return:
        """
        self.data_base = sqlite3.connect(self.name)
        self.cursor = self.data_base.cursor()

    def close_the_data_base(self):
        """
        Close the dataBase
        :return:
        """
        self.data_base.commit()
        self.data_base.close()
