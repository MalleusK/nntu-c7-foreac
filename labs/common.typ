#import "../nntu-typst/nntu.typ" as nntu-template
#import "../nntu-typst/nntu.typ": np

#let report(title: [], number: none, option: none, body) = {
  let student_group = sys.inputs.at(
    "student_group",
    default: none,
  )

  nntu-template.report(
    type: [лабораторной работе],
    title: title,
    number: number,
    option: option,
    name: [Лабораторная работа #number~],
    designation: [
      ЛР-ИРИТ-11.03.03-(#student_group)#if option != none [-#option]
    ],
    institute: [Институт радиоэлектроники и информационных технологий],
    department: [Компьютерные технологии в проектировании и производстве],
    descipline: [Основы радиоэлектроники и связи],
    organization: [
      ИРИТ, каф.КТПП,\
      гр. #student_group
    ],
    body,
  )
}
