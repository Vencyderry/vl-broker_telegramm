from telegrinder.tools import bold, escape, HTMLFormatter, link

ERROR_PERMISSION = "❌ Данную команду может использовать только администратор."
ERROR_TARGET = "❌ Пользователь не найден."
ERROR_COOLDOWN_RULES = "🔹Вы недавно запросили правила чата, повторите позже."

GREETING_JOIN_CHAT = f"""
{HTMLFormatter(bold('🔹Приветствуем в Telegram-чате VL-BROKER l VLB!'))}

{HTMLFormatter(escape('В нём наши участники обсуждают актуальные новости и изменениями в таможенном законодательстве и помогают друг другу.'))}
{HTMLFormatter(escape('📌Хотим обратить Ваше внимание, что у нас есть полезный '))}{HTMLFormatter(link('https://t.me/vlbroker', 'Telegram-канал'))}{HTMLFormatter(escape(' — присоединяйтесь!'))}

{HTMLFormatter(escape('🔹Важно! В чате существуют правила. Обязательно ознакомьтесь с ними.'))}

{HTMLFormatter(bold('Если вам понадобится консультация по таможенному оформлению, то Вы можете обратиться к нам любым из удобных для Вас способом:'))}
{HTMLFormatter(escape('📞8 (800) 600-58-75'))}
{HTMLFormatter(escape('📲8 (951) 018-11-18 (WA)'))}
{HTMLFormatter(escape('📩vlb.cargo@gmail.com'))}
{HTMLFormatter(escape('🌐vlb-broker.ru'))}

{HTMLFormatter(escape('#VLB_СЕРВИС'))}
"""

MESSAGE_RULES = """
Правила общения в Telegram-чате VL-BROKER

🔹Уважаемые партнёры и подписчики, мы разработали правила общения в нашем чате. Просим вас отнестись с уважением к нашей работе и участникам чата.

В чате VL-BROKER разрешается:
*️⃣Общаться, делиться информацией и обсуждать темы, которые относятся к таможенному оформлению, таможенному законодательству, импортируемых товаров и т.п., а также совершать любые другие действия не нарушающие запреты, обозначенные ниже.
*️⃣Предлагать улучшения работы чата, обращать внимание администраторов на нарушения участниками правил в чате.

В чате VL-BROKER запрещаются:
*️⃣Использование оценочных характеристик в адрес любых компаний.
*️⃣Мат как прямой, так и завуалированный.
*️⃣Спамить, флудить и распространять рекламу.
*️⃣Организовывать финансовые операции.
*️⃣Распространять угрозы и оскорбления, устраивать "разборки" или "выяснения отношений".
*️⃣Разглашение личной информации участников чата или третьих лиц без их согласия.
*️⃣Любые формы мошенничества и попрошайничества.
*️⃣Дискриминация по расовому, национальному, религиозному или иному признаку. В том числе националистические, расовые лозунги и высказывания.
*️⃣Пропаганда насилия, оружия, наркотиков и т.д.
*️⃣Отправлять какие-либо сообщения и комментарии, размещать изображения или использовать ники, оскорбляющие общепринятые нормы нравственности.
*️⃣Отправлять какие-либо сообщения и комментарии с призывами и/или обсуждениями возможности нарушения действующего законодательства РФ.

В случае нарушений правил чата, наши администраторы в праве:
*️⃣Выносить предупреждение пользователю о недопустимости его поведения.
*️⃣Выносить повторное предупреждение.
*️⃣Удалять сообщения, нарушающие правила чата. 
*️⃣Блокировать участников чата.

📌Не рекомендуется игнорировать просьбы и предупреждения администраторов чата.
📌Оставляем за собой право удалять сообщения и комментарии без объяснения причины. Жалобу на решения администраторов чата вы можете подать через любую другую социальную сеть, в которых зарегистрированы аккаунты нашей компании, или по номеру телефона. 
📌Возможно будут вноситься изменения в "Правила общения в чате VL-BROKER".

С уважением, команда VL-BROKER!
"""



