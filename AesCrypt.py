def get_data_from_user() -> dict:
    print("Зашифрувати(encrypt) чи розшифрувати(decrypt)")
    action = input("E or D: ").strip().lower()
    while action not in ["e", "d", "encrypt", "decrypt"]:
        action = input("E or D: ").strip().lower()
    if action in ["e", "encrypt"]:
        action = "e"
    else:
        action = "d"

    path_to_file = input("Введіть назву або шлях до файла(data.txt / data.txt.aes): ")
    password = input("Введіть пароль для файла: ")
    output_file_name = input("Введіть назву вихідного файла(data.txt / data.txt.aes): ")

    return {"action": action, "pass": password,
            "path": path_to_file, "output": output_file_name}


def cryptFile(action: str, password: str, file: str, output: str) -> None:
    if action == 'e':
        pyAesCrypt.encryptFile(file, output, password)
    else:
        pyAesCrypt.decryptFile(file, output, password)


def main():
    data = get_data_from_user()

    try:
        cryptFile(action=data.get("action"),
                  password=data.get("pass"),
                  file=data.get("path"),
                  output=data.get("output"))
        print("Finish!")

    except ValueError as error:
        print(f'[-] {error}')


if __name__ == '__main__':
    import pyAesCrypt
    main()
# 8443470370:AAFKDV0qXGE2cbUjDo7Y3c2GsBR3G1JkHcY
