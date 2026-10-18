import requests
import zipfile

from pathlib import Path
from typing import Iterable

def mft_encode(data: str, alphabet: Iterable[str]) -> list[int]:
  alphabet = list(alphabet)

  output = []
  for char in data:
    idx = alphabet.index(char)
    output.append(idx)
    alphabet.insert(0, alphabet.pop(idx))
  return output

def mft_decode(data: list[int], alphabet: Iterable[str]) -> str:
  alphabet = list(alphabet)

  output = ""
  for idx in data:
    output += alphabet[idx]
    alphabet.insert(0, alphabet.pop(idx))
  return output

def compress_to_zip(
    input_file: Path,
    output_zip: Path,
    arcname: str | None = None,
    compresslevel: int = 9,
) -> int:
    if arcname is None:
        arcname = input_file.name

    with zipfile.ZipFile(
        output_zip,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=compresslevel,
    ) as zf:
        zf.write(input_file, arcname=arcname)

    return output_zip.stat().st_size


file_path = Path("war_peace_rus.txt")
if not file_path.exists():
  war_peace = requests.get("https://raw.githubusercontent.com/NNTU-CS/RECF-2026/refs/heads/main/Data/war_peace_rus.txt")

  file_content = war_peace.content.decode("utf8")
  file_path.write_text(file_content)
else:
  file_content = file_path.read_text()

alphabet = list(set(file_content))
unary_dict = [("1" * i) + "0" for i in range(len(alphabet))]

file_encoded = mft_encode(file_content, alphabet)
encoded_unary = "".join([
    unary_dict[idx]
    for idx in file_encoded
])

encoded_path = Path("war_peace_rus.mft")
encoded_path.write_text(encoded_unary)

content_unary = "".join([
    unary_dict[idx]
    for idx in map(alphabet.index, file_content)
])

print(f"Orignal / encoded lenght: {len(content_unary)} / {len(encoded_unary)} ({len(content_unary) / len(encoded_unary)})")

compressed_path = Path("war_peace_rus.zip")
compressed_size = compress_to_zip(file_path, compressed_path)

compressed_encoded_path = Path("war_peace_rus.mft.zip")
compressed_encoded_size = compress_to_zip(encoded_path, compressed_encoded_path)

print(f"Encoded compressed / compressed size: {compressed_encoded_size} / {compressed_size} ({compressed_encoded_size / compressed_size})")