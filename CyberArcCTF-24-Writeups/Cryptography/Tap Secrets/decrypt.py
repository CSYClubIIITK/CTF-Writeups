import csv

char_mapping = {
    '2': 'A', '22': 'B', '222': 'C',
    '3': 'D', '33': 'E', '333': 'F',
    '4': 'G', '44': 'H', '444': 'I',
    '5': 'J', '55': 'K', '555': 'L',
    '6': 'M', '66': 'N', '666': 'O',
    '7': 'P', '77': 'Q', '777': 'R', '7777': 'S',
    '8': 'T', '88': 'U', '888': 'V',
    '9': 'W', '99': 'X', '999': 'Y', '9999': 'Z',
    '0': ' '
}

def decode_message(encoded_message):
    encoded_numbers = encoded_message.split()
    decoded_message = ''.join(char_mapping.get(num, '') for num in encoded_numbers)
    return decoded_message

csv_file_path = 'suspicious_call_log.csv'
output_file_path = 'decoded_messages.txt'

with open(csv_file_path, mode='r') as file:
    reader = csv.DictReader(file)
    with open(output_file_path, mode='w') as output_file:
        for row in reader:
            encoded_numbers = row['Number Dialed']
            decoded_message = decode_message(encoded_numbers)
            output_file.write(decoded_message + '\n')

