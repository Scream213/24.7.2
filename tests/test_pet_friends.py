from api import PetFriends
from settings import valid_email, valid_password
import os
import requests  # Импортируем requests для работы с HTTP-запросами

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Старк', animal_type='Пёс',
                                     age='8', pet_photo='images/amstaff.jpg'):
    """ Проверяем что можно добавить питомца с корректными данными """
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] == name


def test_successful_update_self_pet_info(name='Старк', animal_type='Пёс', age=8):
    """ Проверяем возможность обновления информации о питомце """
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 200
        assert result['name'] == name


def test_successful_delete_self_pet():
    """ Проверяем возможность удаления питомца """
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Старк", "Пёс", "8", "images/amstaff.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    assert status == 200
    assert pet_id not in [pet['id'] for pet in my_pets['pets']]



def test_get_api_key_for_invalid_user():
    """ Проверяем, что неверные учетные данные возвращают ошибку """
    status, result = pf.get_api_key("invalid_email", "invalid_password")
    assert status != 200
    assert 'key' not in result


def test_get_all_pets_without_auth():
    """ Проверяем, что запрос всех питомцев без авторизации возвращает ошибку """
    response = requests.get(pf.base_url + 'api/pets')
    assert response.status_code != 200


def test_add_pet_without_photo():
    """ Проверяем, что можно добавить питомца без фотографии """
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, 'Собака', 'Дворняга', '5', '')
    assert status == 200
    assert result['name'] == 'Собака'


def test_add_pet_with_negative_age():
    """ Проверяем, что попытка добавить питомца с отрицательным возрастом возвращает ошибку """
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, 'Собака', 'Дворняга', '-5', 'images/amstaff.jpg')
    assert status != 200


def test_add_pet_with_invalid_data():
    """ Проверяем, что попытка добавить питомца с недопустимыми данными возвращает ошибку """
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, '', '', '', 'images/amstaff.jpg')
    assert status != 200


def test_update_pet_info_missing_fields():
    """ Проверяем, что попытка обновить питомца без необходимых полей возвращает ошибку """
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) > 0:
        pet_id = my_pets['pets'][0]['id']
        status, result = pf.update_pet_info(auth_key, pet_id, '', '', '')
        assert status != 200


def test_delete_pet_with_unauthorized_user():
    """ Проверяем, что попытка удалить питомца без авторизации возвращает ошибку """
    _, my_pets = pf.get_list_of_pets("unauthorized_auth_key", "my_pets")
    assert my_pets is None


def test_get_pets_filter_my_pets():
    """ Проверяем, что фильтрация по 'my_pets' возвращает только своих питомцев """
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter='my_pets')

    assert status == 200
    assert all(pet['owner_id'] == auth_key['key'] for pet in result['pets'])


def test_update_pet_info_with_invalid_fields():
    """ Проверяем, что обновление информации о питомце с некорректными данными возвращает ошибку """
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], 'invalid_type', 'Пёс', 'not_a_number')
        assert status != 200


def test_get_pet_photo_without_auth():
    """ Проверяем, что получение фотографии питомца без авторизации возвращает ошибку """
    response = requests.get(pf.base_url + 'api/pets/1/photo')
    assert response.status_code != 200
