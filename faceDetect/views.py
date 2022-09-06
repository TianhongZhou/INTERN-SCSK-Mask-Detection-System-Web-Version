import datetime
import socket
from logging import handlers
from django.shortcuts import render
from . import detectMaskWithBase64
import logging
from jsonformatter import JsonFormatter


STRING_FORMAT = '''{
    "@timestamp":  "asctime",
    "Module":      "module",
    "Lineno":      "lineno",
    "Level":       "levelname",
    "Message":     "message"
}'''


def log_json(message):
    ip = socket.gethostbyname(socket.gethostname())
    filename = './logs/' + str(datetime.date.today()) + str(ip) + '.log'
    logger = logging.getLogger(filename)
    logger.setLevel(logging.INFO)

    formatter = JsonFormatter(STRING_FORMAT, indent=4, ensure_ascii=False)
    file_handler = handlers.TimedRotatingFileHandler(filename=filename, when='midnight', backupCount=0, encoding='utf-8')

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info(message)
    logger.removeHandler(file_handler)


def get_video(request):
    if request.method == "POST":
        method = request.POST.get("method")
        base64string = request.POST.get("img")
        t1 = float(request.POST.get("t1"))
        t2 = float(request.POST.get("t2"))

        if method == "Baidu":
            result, number_of_people, score = detectMaskWithBase64.baidu_API_fingMask(base64string)

            if result == "Wearing mask":
                if score >= t1:
                    response = "マスクをかぶって"
                elif (score >= t2) & (score < t1):
                    response = "手作業で点検してください"
                else:
                    response = "マスクを着用していない"
            elif result == "No mask":
                response = "マスクを着用していない"
            else:
                response = "誰も検出されませんでした"

            # log(result_log + ', Using Baidu', 'info')
            result_log = {
                            "Number of People": number_of_people,
                            "Result": result,
                            "Score": score,
                            "Platform": "Baidu"
                        }
            log_json(result_log)

        elif method == "SNN":
            result, number_of_people, score = detectMaskWithBase64.snn_API_fingMask(base64string)

            if len(result) == 1:
                if result[0] == "mask":
                    if score[0] >= t1:
                        response = "マスクをかぶって"
                    elif (score[0] >= t2) & (score[0] < t1):
                        response = "手作業で点検してください"
                    else:
                        response = "マスクを着用していない"
                elif result[0] == "nomask":
                    response = "マスクを着用していない"
            elif len(result) > 1:
                for i in range(len(result)):
                    if result[i] == "nomask":
                        response = "マスクを着用していない"
                        break
                    else:
                        if score[i] >= t1:
                            response = "マスクをかぶって"
                        elif (score[i] >= t2) & (score[i] < t1):
                            response = "手作業で点検してください"
                            break
                        else:
                            response = "マスクを着用していない"
                            break
            else:
                response = "誰も検出されませんでした"

            # log(result_log + ', Using SNN', 'info')
            result_log = {
                            "Number of People": number_of_people,
                            "Result": result,
                            "Score": score,
                            "Platform": "SNN"
                        }
            log_json(result_log)

        else:
            response = "None"

        return render(request, "getVideo.html", {'result': response, 'img': base64string})

    return render(request, "getVideo.html", )
