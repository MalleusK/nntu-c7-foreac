#import "../common.typ": *
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *

#show: report.with(
  title: [
    Исследование алгоритма сжатия Move-to-Front («стопка книг») \
    и префиксного кодирования текстовых данных
  ],
  number: 2,
)

#show raw.where(block: true): set text(size: 6.5pt)
#show figure.where(kind: raw): set block(breakable: true)
#show: codly-init.with()

#heading(numbering: none)[Введение]

В трактах передачи цифровых данных эффективность использования канала связи определяется объемом избыточности сообщений. Естественный текст обладает локальной контекстной связностью: близлежащие слова строятся из ограниченного набора повторяющихся букв.

Алгоритм Move-to-Front (MTF, «стопка книг») устраняет контекстную избыточность динамически перемещая недавно использованные символы в начало списка. Входной поток преобразуется в малые целые числа. В комбинации с префиксным кодированием это уменьшает число передаваемых двоичных символов и повышает степень сжатия архиваторами.

*Цель работы:* исследование эффективности алгоритма Move-to-Front и префиксного кодирования на примере текста романа «Война и мир», расчет числа передаваемых бит и оценка сжатия алгоритмом Deflate.

*Задачи работы:*
+ адаптировать алгоритм MTF для текста романа «Война и мир»;
+ выбрать префиксный код и закодировать содержимое файла;
+ определить число символов ('0', '1'), передаваемых по каналу связи при прямом кодировании и с MTF;
+ сжать исходный и закодированный файлы архиватором ZIP и сравнить результаты;
+ проанализировать полученные характеристики.

= Теоретические основы

== Алгоритм Move-to-Front

Алгоритм MTF оперирует упорядоченным списком символов алфавита $A = (a_0, a_1, dots, a_(m-1))$ мощностью $m$.

При считывании очередного символа находится его текущий индекс $i in [0, m - 1]$ в списке. Значение $i$ выводится на выход, после чего символ переносится на нулевую позицию со сдвигом остальных элементов вправо.

В силу контекстной повторяемости слов символы кодируются малыми индексами ($0, 1, 2, dots$). Выходной поток получает монотонно спадающее распределение вероятностей.

== Префиксный унарный код

Для кодирования номеров выбран унарный префиксный код:

$ C(i) = underbrace(11 dots 1, i) 0. $ <eq:unary>

Длина кодового слова для индекса $i$:

$ L(i) = i + 1 quad ["бит"]. $ <eq:unary_len>

Символ `0` является маркером окончания слова, что обеспечивает однозначное префиксное декодирование. Малые индексы получают минимальную разрядность: $C(0) = "0"$, $C(1) = "10"$, $C(2) = "110"$.

== Оценка сжатия Deflate

Для проверки сжимаемости использовался алгоритм Deflate (ZIP), объединяющий LZ77 и код Хаффмана. Коэффициент сжатия:

$ K_("сжат") = V_("исх") / V_("zip"). $ <eq:k_zip>

= Ход работы

+ Был взят текст романа «Война и мир» на русском языке (`war_peace_rus.txt`) объемом $1 thin 908 thin 695$ байт ($m = 137$ символов).
+ Были реализованы функции `mft_encode`, `mft_decode` и `compress_to_zip`.
+ Сформирован массив унарных кодов `unary_dict`.
+ Выполнено MTF-кодирование текста романа. Индексы преобразованы в унарную битовую строку и записаны в `war_peace_rus.mft`.
+ Выполнено прямое унарное кодирование текста без MTF.
+ Подсчитано суммарное количество символов `'0'` и `'1'` для обоих вариантов передачи.
+ Исходный и закодированный файлы сжаты архиватором ZIP (`compresslevel = 9`). Вычислены коэффициенты сжатия.

= Листинг программы

Исходный код разработанных функций приведен в @lst:mtf_funcs[листинге], а сценарий кодирования текста романа и замера объемов данных — в @lst:mtf_main[листинге].

#figure(
  ```python
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
  ```,
  caption: [Функции алгоритма Move-to-Front и компрессии в формат ZIP],
) <lst:mtf_funcs>

#pagebreak()

#figure(
  ```python
  file_path = Path("war_peace_rus.txt")
  if not file_path.exists():
      war_peace = requests.get(
          "https://raw.githubusercontent.com/NNTU-CS/RECF-2026/refs/heads/main/Data/war_peace_rus.txt"
      )
      file_content = war_peace.content.decode("utf8")
      file_path.write_text(file_content)
  else:
      file_content = file_path.read_text()

  alphabet = list(set(file_content))
  unary_dict = [("1" * i) + "0" for i in range(len(alphabet))]

  file_encoded = mft_encode(file_content, alphabet)
  encoded_unary = "".join([unary_dict[idx] for idx in file_encoded])

  encoded_path = Path("war_peace_rus.mft")
  encoded_path.write_text(encoded_unary)

  content_unary = "".join([
      unary_dict[idx]
      for idx in map(alphabet.index, file_content)
  ])

  print(f"Original / encoded length: {len(content_unary)} / {len(encoded_unary)} "
        f"({len(content_unary) / len(encoded_unary):.3f})")

  compressed_path = Path("war_peace_rus.zip")
  compressed_size = compress_to_zip(file_path, compressed_path)

  compressed_encoded_path = Path("war_peace_rus.mft.zip")
  compressed_encoded_size = compress_to_zip(encoded_path, compressed_encoded_path)

  print(f"Encoded compressed / compressed size: {compressed_encoded_size} / {compressed_size} "
        f"({compressed_encoded_size / compressed_size:.3f})")
  ```,
  caption: [Сценарий кодирования текста романа и замера объемов данных],
) <lst:mtf_main>

= Итоги работы программы

Результаты эксперимента сведены в @tbl:results.

#figure(
  table(
    columns: (2.4fr, 1.3fr, 1.3fr, 1.4fr),
    align: (left, center, center, center),
    stroke: 0.5pt + luma(150),
    fill: (x, y) => if y == 0 { luma(240) } else { none },
    table.header(
      [*Параметр*],
      [*Без MTF (исходный)*],
      [*С алгоритмом MTF*],
      [*Соотношение / Выигрыш*],
    ),
    [Длина текста $N$, символов], [1 908 695], [1 908 695], [1.000],
    [Мощность алфавита $m$], [137], [137], [---],
    [Бит в канале связи ('0', '1')], [146 319 495], [26 158 085], [*в 5.594 раза* (экономия 82.1%)],
    [Средняя длина на символ], [76.66 бит], [13.71 бит], [уменьшение в 5.594 раза],
    [Размер файла на диске], [1 908 695 байт], [26 158 085 байт], [файл `.mft` (ASCII-символы)],
    [Размер ZIP-архива (Deflate)], [753 130 байт], [1 696 840 байт], [2.253],
    [Коэффициент сжатия $K_("сжат")$], [*2.534*], [*15.416*], [*рост в 6.08 раза*],
  ),
  caption: [Результаты кодирования и сжатия романа «Война и мир»],
) <tbl:results>

== Анализ полученных результатов

Прямое унарное кодирование текста без предварительной обработки требует передачи $146 thin 319 thin 495$ бит по каналу связи. Редкие символы алфавита получают длинные кодовые слова из десятков единиц.

Применение алгоритма MTF снизило объем передаваемых бит до $26 thin 158 thin 085$. Получен выигрыш в $5.594$ раза так как основная масса символов закодирована первыми индексами стопки.

При сжатии архиватором Deflate исходный текст показал коэффициент $K_("исх") = 2.534$. Закодированный файл `war_peace_rus.mft` был сжат с коэффициентом $K_("mft") = 15.416$ (в $6.08$ раза выше). Высокая компрессия обусловлена тем, что унарная последовательность после MTF состоит из длинных серий '1' и редких '0', эффективно сжимаемых алгоритмом LZ77.

#heading(numbering: none)[Выводы]

+ Проведена адаптация алгоритма Move-to-Front для русского текста романа «Война и мир» объемом $1.91$ млн символов.
+ В качестве префиксного кода выбран унарный код $C(i) = "1"^i"0"$, обеспечивающий однозначное декодирование.
+ Алгоритм MTF снижает число передаваемых по каналу двоичных символов со $146 thin 319 thin 495$ до $26 thin 158 thin 085$ бит (выигрыш в $5.594$ раза или $82.1\%$).
+ Коэффициент сжатия Deflate для MTF-файла составил $15.416$ против $2.534$ для исходного текста, что подтверждает эффективность применения MTF перед словарными алгоритмами.
