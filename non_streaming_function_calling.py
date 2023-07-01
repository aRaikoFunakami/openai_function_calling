import openai
import json
import os
import logging
import inspect

#
# Config
#
model="gpt-3.5-turbo-0613"

# load config
def load_config():
    config_file = os.path.dirname(__file__) + "/config.json"
    config = None
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config

#
# chatGPTが自動的に選択する関数
#

#緯度と経度の情報から現在の天気を取得する
def get_weather_info(latitude, longitude):
	return inspect.currentframe().f_code.co_name

weather_function = {
    "name": "get_weather_info",
    "description": "緯度と経度の情報から現在の天気を取得する",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {
                "type": "string",
                "description": "緯度の情報",
            },
            "longitude": {
                "type": "string",
                "description": "経度の情報",
            },
        },
        "required": ["latitude", "longitude"],
    },
}

#カーナビの使用方法についての質問からカーナビの使い方を取得する
def get_carnavi_info(query):
	return inspect.currentframe().f_code.co_name

carnavi_function = {
    "name": "get_carnavi_info",
    "description": "インターネット接続機能を持ったカーナビの使用方法についての質問からカーナビの取り扱い説明書を取得する",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "カーナビの使用方法についての質問",
            },
        },
        "required": ["query"],
    },
}

#車の使用方法についての質問から車の使い方を取得する
def get_vehicle_info(query):
	return inspect.currentframe().f_code.co_name

vehicle_function = {
    "name": "get_vehicle_info",
    "description": "車の使用方法についての質問から車の取り扱い説明書を取得する",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "車の使用方法についての質問",
            },
        },
        "required": ["query"],
    },
}

def call_defined_function(message):
    function_name = message["function_call"]["name"]
    arguments=json.loads(message["function_call"]["arguments"])
    logging.debug("選択された関数を呼び出す: %s", function_name)
    if function_name == "get_weather_info":
        return get_weather_info(
            latitude=arguments.get("latitude"),
            longitude=arguments.get("longitude"),
        )
    elif function_name == "get_carnavi_info":
        return get_carnavi_info(query = arguments.get("query"))
    elif function_name == "get_vehicle_info":
        return get_vehicle_info(query = arguments.get("query"))
    else:
        return None

def non_streaming_chat(text):
    # 関数と引数を決定する
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": text}],
            functions=[weather_function, carnavi_function, vehicle_function],
            function_call="auto",
        )
    except openai.error.OpenAIError as e:
        error_string = f"An error occurred: {e}"
        print(error_string)
        return { "response": error_string, "finish_reason": "stop" }

    message = response["choices"][0]["message"]
    logging.debug("message: %s", message)
    # 選択した関数を実行する
    if message.get("function_call"):
        function_response = call_defined_function(message)
        #
        # 関数のレスポンスをベースに ChatGPT に回答を作成させる
        # 今回は何もしない
        #
        return function_response
    else:
        return "chatgpt"

guess_prompt = '''
あなたは車の運転中です。
車にはカーナビがセットアップされています。
車のカーナビにはインターネット接続機能があります。
車のカーナビにはWebブラウザがインストールされています。
次の入力文からどのような状況にあるか50文字以内で答えよ
入力文:{}
'''

guess_template =''''
次の状況と条件を踏まえて入力文について答えよ。

状況:
{}

条件:
- 50文字以内で回答せよ

入力文:
{}
'''

def guess_situation(query):
    print(query)
    prompt = guess_prompt.format(query)
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
    except openai.error.OpenAIError as e:
        print(f"Exception: {e}")
        return e

    message = response["choices"][0]["message"]
    logging.info("content: %s", message.get("content"))
    return message.get("content")


def chat(text):
    logging.debug(f"chatstart:{text}")
    config = load_config()
    openai.api_key = config["openai_api_key"]
    # situation = guess_situation(text)
    # q = guess_template.format(situation, text)
    q = template.format(text)
    return non_streaming_chat(q)

template =''''
あなたは車の運転中です。
あなたはカーナビを利用しています。
あなたはカーナビでインターネットが利用できます。
あなたはカーナビでWebブラウザが利用できます。
ガソリンを入れる蓋の位置は車の取り扱い説明書に記載されています。
次の条件を踏まえて入力文について答えよ。

条件:
- 50文字以内で回答せよ

入力文:
{}
'''

queries2 = [
    ["織田信長について10文字で答えよ", "chatgpt"],
	["横浜の今日の天気を教えてください", "get_weather_info"],
	["インターネットを使いたい", "get_carnavi_info"],
	["ガソリンの蓋が左右どちらにあるのか教えて", "get_vehicle_info"],
]

queries = [
	["燃料タンクの容量は？", "get_vehicle_info"],
	["オイル交換時期は？", "get_vehicle_info"],
	["タイヤの適切な空気圧は？", "get_vehicle_info"],
	["バッテリーの寿命は？", "get_vehicle_info"],
	["最新地図データはどこで入手できますか？", "get_carnavi_info"],
	["目的地設定方法は？", "get_carnavi_info"],
	["渋滞情報の表示方法は？", "get_carnavi_info"],
	["Bluetooth接続方法は？", "get_carnavi_info"],
	["明日の天気は？", "get_weather_info"],
	["現在の気温は？", "get_weather_info"],
	["週末の天気予報は？", "get_weather_info"],
	["都市Aの明後日の降水確率は？", "get_weather_info"],
	["最近の科学ニュースは？", "chatgpt"],
	["好きな映画は何ですか？", "chatgpt"],
	["人工知能の仕組みは？", "chatgpt"],
	["ヘルシーなレシピを教えてください", "chatgpt"]
]


def main():
	logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(filename)s:%(funcName)s[%(lineno)d] - %(message)s")
	for query in queries:
		response = chat(query[0])
		print(f"[{query[1] == response}] 期待:{query[1]}, 実際:{response}, 質問:{query[0]}")

if __name__ == '__main__':
    main()