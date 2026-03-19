#!/usr/bin/env python3
"""
AI 单词记忆技巧生成模块
基于大模型生成单词的音、形、例句、图片描述、短视频脚本、记忆文字、挖空练习
"""

import json
import os
import random
import base64
from typing import Dict, List, Any

# 尝试导入 HTTP 库
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class AIMemoryGenerator:
    """AI 单词记忆技巧生成器"""
    
    def __init__(self, api_key: str = None, model: str = 'qwen'):
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY', '')
        self.model = model
        self.base_url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
        
        # Azure TTS 配置
        self.azure_tts_key = os.getenv('AZURE_TTS_KEY', '')
        self.azure_tts_region = os.getenv('AZURE_TTS_REGION', 'eastus')
        
        # AI 绘画配置（纳米香蕉/纳米果果）
        self.nanobanana_api_key = os.getenv('NANOBANANA_API_KEY', '')
        self.nanobanana_url = os.getenv('NANOBANANA_URL', 'https://api.nanobanana.pro/v1')
    
    def generate_memory_techniques(self, words: List[Dict]) -> Dict:
        """
        为单词列表生成记忆技巧
        
        Args:
            words: [{'english': 'apple', 'chinese': '苹果', 'synonym': 'fruit'}]
        
        Returns:
            {
                'success': bool,
                'techniques': [
                    {
                        'word': 'apple',
                        'phonetic': '/ˈæp.əl/',
                        'audio_tip': '发音类似'爱剖'',
                        'shape_tip': 'a-pp-le，像一个人 (a) 拿着两个苹果 (pp)',
                        'example_sentences': [...],
                        'image_prompt': '...',
                        'video_script': '...',
                        'memory_story': '...',
                        'fill_blank_exercise': '...'
                    }
                ]
            }
        """
        if not HAS_REQUESTS:
            return {'success': False, 'error': '请安装 requests 库：pip install requests'}
        
        if not self.api_key:
            # 返回模拟数据
            return self._generate_mock_techniques(words)
        
        try:
            # 构建 Prompt
            prompt = self._build_prompt(words)
            
            # 调用通义千问 API
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'qwen-max',
                'input': {
                    'messages': [
                        {
                            'role': 'system',
                            'content': '你是一位专业的英语单词记忆教练，擅长用创意方法帮助学生记忆单词。请为每个单词生成：1.音标 2.发音技巧 3.字形记忆法 4.3 个例句 5.AI 绘画提示词 6.短视频脚本 7.记忆故事 8.挖空练习。返回 JSON 格式。'
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ]
                },
                'parameters': {
                    'result_format': 'message',
                    'temperature': 0.7
                }
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result['output']['choices'][0]['message']['content']
            
            # 解析 JSON 响应
            techniques = json.loads(content)
            
            return {'success': True, 'techniques': techniques}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _build_prompt(self, words: List[Dict]) -> str:
        """构建 AI Prompt"""
        word_list = ', '.join([f"{w['english']}({w['chinese']})" for w in words[:10]])
        
        return f"""
请为以下英语单词生成记忆技巧：

{word_list}

为每个单词生成以下信息，返回 JSON 数组格式：
[
  {{
    "word": "单词",
    "phonetic": "音标",
    "audio_tip": "发音技巧（谐音/联想）",
    "shape_tip": "字形记忆法（拆字/联想）",
    "example_sentences": [
      {{"en": "英文例句", "zh": "中文翻译"}}
    ],
    "image_prompt": "AI 绘画提示词（英文，描述单词场景）",
    "video_script": "15 秒短视频脚本",
    "memory_story": "包含所有单词的连贯故事（200 字）",
    "fill_blank_text": "包含所有单词的段落，单词处用____替换",
    "fill_blank_answers": ["答案 1", "答案 2"]
  }}
]
"""
    
    def _generate_mock_techniques(self, words: List[Dict]) -> Dict:
        """生成模拟数据（无 API 时）"""
        techniques = []
        
        # 示例数据模板
        templates = {
            'apple': {
                'phonetic': '/ˈæp.əl/',
                'audio_tip': '发音类似"爱剖"，想象爱剖苹果吃',
                'shape_tip': 'a-pp-le，像一个人 (a) 拿着两个苹果 (pp)',
                'example_sentences': [
                    {'en': 'I eat an apple every day.', 'zh': '我每天吃一个苹果。'},
                    {'en': 'This apple is sweet.', 'zh': '这个苹果很甜。'},
                    {'en': 'She peeled the apple.', 'zh': '她削了苹果皮。'}
                ],
                'image_prompt': 'A red shiny apple on a wooden table, natural lighting, photorealistic, 4k',
                'video_script': '【0-3 秒】镜头对准苹果特写【4-10 秒】切开苹果展示果肉【11-15 秒】咬一口说"Apple, 苹果"',
                'memory_story': '小明早上起来，拿起一个红红的 apple（苹果），开心地咬了一口。这个 apple 非常甜，让他一整天都心情愉快。',
                'fill_blank_text': 'I eat an ____ every day. This ____ is sweet.',
                'fill_blank_answers': ['apple', 'apple']
            },
            'banana': {
                'phonetic': '/bəˈnæn.ə/',
                'audio_tip': '发音类似"不拿呢"，想象不拿香蕉才怪',
                'shape_tip': 'banana 里有 3 个"a"，像香蕉的形状弯弯的',
                'example_sentences': [
                    {'en': 'Monkeys love bananas.', 'zh': '猴子喜欢香蕉。'},
                    {'en': 'This banana is ripe.', 'zh': '这根香蕉熟了。'},
                    {'en': 'She added banana to the smoothie.', 'zh': '她把香蕉加到冰沙里。'}
                ],
                'image_prompt': 'A bunch of yellow bananas hanging, tropical background, bright colors, illustration style',
                'video_script': '【0-3 秒】猴子拿着香蕉【4-10 秒】剥开香蕉皮【11-15 秒】吃香蕉说"Banana, 香蕉"',
                'memory_story': '动物园里，小猴子看到一根黄色的 banana（香蕉），兴奋地跳起来。它快速剥开 banana 的皮，开心地吃了起来。',
                'fill_blank_text': 'Monkeys love ____. This ____ is ripe.',
                'fill_blank_answers': ['bananas', 'banana']
            },
            'orange': {
                'phonetic': '/ˈɔːr.ɪndʒ/',
                'audio_tip': '发音类似"奥润吉"，想象橙子的颜色橙红色',
                'shape_tip': 'o-range，o 像橙子的圆形，range 表示范围（橙子有很多瓣）',
                'example_sentences': [
                    {'en': 'Orange is my favorite color.', 'zh': '橙色是我最喜欢的颜色。'},
                    {'en': 'This orange is juicy.', 'zh': '这个橙子很多汁。'},
                    {'en': 'She drank orange juice.', 'zh': '她喝了橙汁。'}
                ],
                'image_prompt': 'Fresh orange fruit sliced, showing juicy segments, white background, studio lighting',
                'video_script': '【0-3 秒】橙子特写旋转【4-10 秒】切开橙子展示汁水【11-15 秒】挤橙汁说"Orange, 橙子"',
                'memory_story': '水果店里，有一个大大的 orange（橙子）。小明拿起这个 orange，闻到清新的香味，忍不住买了下来。',
                'fill_blank_text': '____ is my favorite color. This ____ is juicy.',
                'fill_blank_answers': ['Orange', 'orange']
            }
        }
        
        for word in words:
            english = word['english'].lower()
            technique = templates.get(english, self._generate_generic_technique(word))
            technique['word'] = word['english']
            techniques.append(technique)
        
        return {'success': True, 'techniques': techniques}
    
    def _generate_generic_technique(self, word: Dict) -> Dict:
        """生成通用记忆技巧模板"""
        english = word['english']
        chinese = word['chinese']
        
        return {
            'phonetic': f'/{english}/',
            'audio_tip': f'多听多读，注意发音部位',
            'shape_tip': f'拆分记忆：{english[:3]}-{english[3:]}',
            'example_sentences': [
                {'en': f'This is a {english}.', 'zh': f'这是一个{chinese}。'},
                {'en': f'I like {english}.', 'zh': f'我喜欢{chinese}。'},
                {'en': f'The {english} is good.', 'zh': f'这个{chinese}很好。'}
            ],
            'image_prompt': f'A {english}, photorealistic, detailed, 4k',
            'video_script': f'展示{chinese}，介绍用法',
            'memory_story': f'小明遇到了一个{english}（{chinese}），他仔细观察，记住了这个单词。',
            'fill_blank_text': f'This is a ____. I like ____.',
            'fill_blank_answers': [english, english]
        }
    
    def generate_word_image(self, word: str, image_prompt: str) -> Dict:
        """
        调用 AI 绘画生成单词图片
        
        Args:
            word: 英文单词
            image_prompt: AI 绘画提示词
        
        Returns:
            {
                'success': bool,
                'image_url': str,
                'image_base64': str (可选)
            }
        """
        if not HAS_REQUESTS:
            return {'success': False, 'error': '请安装 requests 库'}
        
        try:
            # 调用纳米香蕉 API（示例）
            headers = {
                'Authorization': f'Bearer {self.nanobanana_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'prompt': image_prompt,
                'model': 'nano-banana-pro-2',
                'size': '1024x1024',
                'n': 1
            }
            
            response = requests.post(
                f'{self.nanobanana_url}/images/generations',
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            image_url = result['data'][0]['url']
            
            return {'success': True, 'image_url': image_url}
            
        except Exception as e:
            # 返回模拟图片（占位图）
            return {
                'success': True,
                'image_url': f'https://via.placeholder.com/512x512.png?text={word}',
                'warning': '使用占位图 - 请配置 AI 绘画 API'
            }
    
    def generate_word_audio(self, word: str, text: str = None) -> Dict:
        """
        调用 Azure TTS 生成单词发音
        
        Args:
            word: 英文单词
            text: 要朗读的文本（默认为单词本身）
        
        Returns:
            {
                'success': bool,
                'audio_url': str (data:audio/mp3;base64,...),
                'duration': float
            }
        """
        if not HAS_REQUESTS:
            return {'success': False, 'error': '请安装 requests 库'}
        
        if not self.azure_tts_key or self.azure_tts_key == 'YOUR_AZURE_TTS_KEY':
            # 返回模拟音频
            return {
                'success': True,
                'audio_url': 'data:audio/mp3;base64,SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4LjI5LjEwMA',
                'duration': 1.0,
                'warning': '模拟音频 - 请配置 Azure TTS'
            }
        
        try:
            # Azure TTS API
            headers = {
                'Ocp-Apim-Subscription-Key': self.azure_tts_key,
                'Content-Type': 'application/ssml+xml',
                'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3'
            }
            
            ssml = f"""
            <speak version='1.0' xml:lang='en-US'>
                <voice xml:lang='en-US' xml:gender='Female' name='en-US-JennyNeural'>
                    {text or word}
                </voice>
            </speak>
            """
            
            response = requests.post(
                f'https://{self.azure_tts_region}.tts.speech.microsoft.com/cognitiveservices/v1',
                headers=headers,
                data=ssml.encode('utf-8'),
                timeout=10
            )
            response.raise_for_status()
            
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            
            return {
                'success': True,
                'audio_url': f'data:audio/mp3;base64,{audio_base64}',
                'duration': len(response.content) / 16000  # 估算时长
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_english_story(self, words: List[Dict], level: str = 'B1', style: str = 'story') -> Dict:
        """
        生成英文故事（包含所有错词）
        
        Args:
            words: 错词列表 [{'english': 'apple', 'chinese': '苹果'}]
            level: 英语难度 (A1/A2/B1/B2/C1/C2)
            style: 故事风格 (suspense/horror/comedy/news/fairy/scifi)
        
        Returns:
            {
                'success': bool,
                'story': {
                    'title': str,
                    'content_en': str,
                    'content_zh': str,
                    'word_count': int,
                    'level': str,
                    'style': str,
                    'words_used': [str],
                    'audio_url': str (可选)
                }
            }
        """
        if not HAS_REQUESTS:
            return {'success': False, 'error': '请安装 requests 库'}
        
        if not self.api_key:
            # 返回模拟故事
            return self._generate_mock_story(words, level, style)
        
        try:
            # 构建 Prompt
            word_list = ', '.join([f"{w['english']}({w['chinese']})" for w in words])
            
            style_prompts = {
                'suspense': '悬疑风格，充满未知和紧张感',
                'horror': '恐怖风格，营造惊悚氛围',
                'comedy': '脱口秀风格，幽默搞笑',
                'news': '新闻稿风格，正式客观',
                'fairy': '童话故事风格，温馨梦幻',
                'scifi': '科幻风格，未来感十足'
            }
            
            level_prompts = {
                'A1': '使用最简单的词汇和短句（50-80 词）',
                'A2': '使用基础词汇和简单句（80-120 词）',
                'B1': '使用中等难度词汇（120-180 词）',
                'B2': '使用较复杂词汇和从句（180-250 词）',
                'C1': '使用高级词汇和复杂句式（250-350 词）',
                'C2': '使用母语级表达（350-500 词）'
            }
            
            prompt = f"""
请用英文创作一个{style_prompts.get(style, '有趣的')}故事。

必须包含以下单词：{word_list}

难度要求：{level_prompts.get(level, '中等难度')}

返回 JSON 格式：
{{
  "title": "故事标题",
  "content_en": "英文故事正文",
  "content_zh": "中文翻译",
  "word_count": 词数统计，
  "words_used": ["列出用到的目标单词"]
}}
"""
            
            # 调用通义千问 API
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'qwen-max',
                'input': {
                    'messages': [
                        {
                            'role': 'system',
                            'content': '你是一位专业的英语教育作家，擅长创作适合不同水平的英语学习故事。'
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ]
                },
                'parameters': {
                    'result_format': 'message',
                    'temperature': 0.8
                }
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result['output']['choices'][0]['message']['content']
            
            # 解析 JSON 响应
            story = json.loads(content)
            story['level'] = level
            story['style'] = style
            
            return {'success': True, 'story': story}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_mock_story(self, words: List[Dict], level: str = 'B1', style: str = 'story') -> Dict:
        """生成模拟故事（无 API 时）"""
        
        style_templates = {
            'suspense': {
                'title': 'The Mysterious Package',
                'en': 'It was a dark night when Tom received a strange package. Inside was an apple, a banana, and an orange. But why these fruits? He felt nervous. Suddenly, the phone rang. "Did you get it?" a voice asked. Tom held his breath. What was "it"? He looked at the fruits again. There must be a secret message hidden in them.',
                'zh': '那是一个漆黑的夜晚，汤姆收到了一个奇怪的包裹。里面有一个苹果、一根香蕉和一个橙子。但为什么是这些水果？他感到紧张。突然，电话响了。"你收到了吗？"一个声音问。汤姆屏住呼吸。"它"是什么？他再次看着那些水果。里面一定隐藏着秘密信息。'
            },
            'horror': {
                'title': 'The Cursed Fruits',
                'en': 'The old witch warned: "Never eat these fruits after midnight." But Lisa didn\'t listen. She took a bite of the apple. Then the banana. Finally the orange. At exactly 12:00 AM, the fruits began to glow. Shadows moved on the wall. A cold voice whispered: "You shouldn\'t have done that..."',
                'zh': '老女巫警告说："午夜后千万不要吃这些水果。"但丽莎没有听。她咬了一口苹果，然后是香蕉，最后是橙子。在午夜 12 点整，水果开始发光。墙上有影子在移动。一个冰冷的声音低语："你不应该那样做……"'
            },
            'comedy': {
                'title': 'My Worst Date Ever',
                'en': 'So I\'m on this date, right? Trying to impress this girl. I brought her an apple - classic, romantic. She said she\'s allergic. Okay, no problem. I pull out a banana. She\'s laughing now. Then I drop the orange and it rolls under the table. I dive after it, hit my head, and that\'s how I ended up in the ER. Best first date ever!',
                'zh': '我在约会，想给这个女孩留下好印象。我带了一个苹果给她——经典，浪漫。她说她过敏。好吧，没问题。我拿出一根香蕉。她现在笑了。然后我把橙子掉在地上，它滚到桌子底下。我扑过去捡，撞到了头，就这样我进了急诊室。有史以来最好的第一次约会！'
            },
            'news': {
                'title': 'Local Student Wins Fruit Essay Contest',
                'en': 'BEIJING, March 18 - A high school student from Beijing has won the national English writing competition with an essay about apples, bananas, and oranges. The judges praised the student\'s creative use of everyday vocabulary. "This demonstrates exceptional language mastery," said chief judge Dr. Smith. The student will represent China in the international competition next month.',
                'zh': '北京 3 月 18 日电 - 一名来自北京的中学生凭借一篇关于苹果、香蕉和橙子的文章获得了全国英语写作比赛冠军。评委们称赞该学生创造性地使用了日常词汇。"这展示了卓越的语言掌握能力，"主评委史密斯博士说。该学生将于下个月代表中国参加国际比赛。'
            },
            'fairy': {
                'title': 'The Magic Garden',
                'en': 'Once upon a time, there was a magical garden where fruits could talk. One day, a little apple said to a banana: "Why are you so curved?" The banana smiled: "Because I\'m always bending to help others." Just then, an orange rolled by: "You\'re both wonderful! Together we make the perfect fruit salad." And they all lived happily ever after.',
                'zh': '从前，有一个神奇的花园，那里的水果会说话。一天，小苹果对香蕉说："你为什么这么弯？"香蕉微笑着说："因为我总是弯腰帮助别人。"就在这时，一个橙子滚了过来："你们都很棒！在一起我们就是完美的水果沙拉。"从此他们幸福地生活在一起。'
            },
            'scifi': {
                'title': 'Mission to Mars',
                'en': 'Commander Zhang checked the cargo manifest one last time. Oxygen levels: stable. Food supplies: apple seeds, banana clones, orange DNA samples. "Are you sure these will grow on Mars?" asked Lieutenant Chen. "They have to," Zhang replied. "These genetically modified fruits are humanity\'s last hope for survival on the red planet."',
                'zh': '张指挥官最后一次检查货物清单。氧气水平：稳定。食物供应：苹果种子、香蕉克隆体、橙子 DNA 样本。"你确定这些能在火星上生长吗？"陈中尉问。"必须能，"张回答。"这些转基因水果是人类在红色星球上生存的最后希望。"'
            }
        }
        
        template = style_templates.get(style, style_templates['fairy'])
        
        # 替换单词（确保使用传入的单词）
        if words:
            word_en = words[0]['english'] if words else 'apple'
            word_zh = words[0]['chinese'] if words else '苹果'
            # 简单替换示例
            template['en'] = template['en'].replace('apple', word_en).replace('Apple', word_en.capitalize())
        
        return {
            'success': True,
            'story': {
                'title': template['title'],
                'content_en': template['en'],
                'content_zh': template['zh'],
                'word_count': len(template['en'].split()),
                'level': level,
                'style': style,
                'words_used': [w['english'] for w in words]
            }
        }
    
    def generate_fill_blank_exercise(self, words: List[Dict], difficulty: str = 'medium') -> Dict:
        """
        生成挖空练习
        
        Args:
            words: 单词列表
            difficulty: easy/medium/hard
        
        Returns:
            {
                'text': '包含挖空的段落',
                'answers': ['答案列表'],
                'hints': ['提示信息']
            }
        """
        # 构建一个连贯的故事
        story_templates = [
            "小明今天去超市购物。他买了很多水果，包括____（{zh}）。回到家后，他把____放在桌子上，准备享用。",
            "在学校里，老师教我们学习新单词。今天的主题是____（{zh}）。同学们都很认真地学习____的用法。",
            "周末，小红去公园野餐。她带了很多食物，其中最喜欢的是____（{zh}）。她和朋友们一起分享了____。"
        ]
        
        template = random.choice(story_templates)
        
        # 替换挖空
        text = template
        answers = []
        hints = []
        
        for word in words[:3]:  # 最多 3 个单词
            text = text.replace('____', word['english'], 1)
            answers.append(word['english'])
            hints.append(word['chinese'])
        
        # 补充剩余的____
        text = text.replace('____', '_______')
        
        return {
            'text': text,
            'answers': answers,
            'hints': hints,
            'difficulty': difficulty
        }


# 全局实例
ai_generator = AIMemoryGenerator()


if __name__ == '__main__':
    # 测试
    test_words = [
        {'english': 'apple', 'chinese': '苹果'},
        {'english': 'banana', 'chinese': '香蕉'},
        {'english': 'orange', 'chinese': '橙子'}
    ]
    
    result = ai_generator.generate_memory_techniques(test_words)
    print(json.dumps(result, ensure_ascii=False, indent=2))
