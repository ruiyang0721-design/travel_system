import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from backend.api.models import Spot, SpotTip


def load_tips():
    """导入景点攻略数据"""
    SpotTip.objects.all().delete()
    print("已清除旧攻略数据")

    tips_data = [
        # 故宫
        {'spot': '故宫博物院', 'username': '李四', 'title': '故宫游玩最佳路线', 'content': '建议从午门进神武门出，沿中轴线走：太和殿→中和殿→保和殿→乾清宫→坤宁宫→御花园。珍宝馆和钟表馆各加10元门票，强烈推荐。全程大概需要4小时，穿舒适的鞋子！早上8:30开门就进，人少拍照好。', 'tip_type': '实用建议', 'likes': 42},
        {'spot': '故宫博物院', 'username': '王五', 'title': '故宫拍照机位分享', 'content': '最佳拍照点：1）太和殿前广场，低角度仰拍超震撼；2）东六宫的红墙小巷，人少光线好；3）御花园的古树和奇石；4）角楼（神武门出来左转护城河边）。建议上午去东六宫拍，下午光线打在红墙上特别美。', 'tip_type': '拍照技巧', 'likes': 35},
        {'spot': '故宫博物院', 'username': '赵六', 'title': '别周末去！', 'content': '血泪教训，周六去的故宫，人山人海根本走不动。工作日去体验感好十倍。另外故宫里没有卖水的地方（只有自动售货机经常排队），建议自带水和零食。', 'tip_type': '避坑指南', 'likes': 58},

        # 天坛
        {'spot': '天坛公园', 'username': '小红', 'title': '天坛早上去看晨练', 'content': '建议早上6-7点到，可以看到北京大爷大妈在天坛晨练，打太极、踢毽子、唱京剧，特别有生活气息。回音壁和圜丘坛一定要试试，站在圆心说话真的有回音。', 'tip_type': '实用建议', 'likes': 23},

        # 兵马俑
        {'spot': '秦始皇兵马俑博物馆', 'username': '王五', 'title': '一定要请导游！', 'content': '兵马俑不请导游等于白去。景区门口有很多野导，建议在官方讲解处请讲解员（150元左右）。一号坑最震撼，三号坑最小但最重要（指挥部）。出来后可以去丽山园看铜车马，包含在门票里但很多人不知道。', 'tip_type': '实用建议', 'likes': 67},
        {'spot': '秦始皇兵马俑博物馆', 'username': '赵六', 'title': '防骗指南', 'content': '景区外面有很多卖玉的店铺说是蓝田玉，大部分是假的不要买。还有人说带你去"真正的兵马俑"，都是骗人的。认准官方售票窗口。坐306路公交车直达最方便。', 'tip_type': '避坑指南', 'likes': 89},

        # 西湖
        {'spot': '西湖', 'username': '小红', 'title': '西湖骑行路线推荐', 'content': '租一辆共享单车绕西湖骑行：断桥→白堤→苏堤→花港观鱼→雷峰塔→长桥→南山路→湖滨路，全程约1.5小时。春天苏堤桃花开了特别美。建议傍晚骑，夕阳洒在湖面上金光闪闪。', 'tip_type': '实用建议', 'likes': 31},
        {'spot': '西湖', 'username': '李四', 'title': '西湖边的美食推荐', 'content': '楼外楼的西湖醋鱼和东坡肉是经典，但价格偏贵。知味观的小吃性价比更高，猫耳朵和片儿川都好吃。如果想吃便宜的，断桥边上有家新丰小吃，小笼包和牛肉粉丝汤很赞。', 'tip_type': '美食推荐', 'likes': 28},

        # 洪崖洞
        {'spot': '洪崖洞', 'username': '王五', 'title': '洪崖洞最佳拍摄时间', 'content': '晚上7-9点灯光最美，千与千寻既视感。最佳拍摄位置在千厮门大桥上，可以拍到洪崖洞全景。对面的大剧院江边也是绝佳机位。注意洪崖洞里面其实就是个商业街，快速逛一圈就好，重点是外面拍夜景。', 'tip_type': '拍照技巧', 'likes': 53},
        {'spot': '洪崖洞', 'username': '赵六', 'title': '洪崖洞避坑', 'content': '不要节假日去！排队能排两小时。里面的东西又贵又不好吃，想吃火锅去附近的居民区找那种苍蝇馆子，味道正宗价格便宜。建议工作日晚上去，人少体验好。', 'tip_type': '避坑指南', 'likes': 44},

        # 外滩
        {'spot': '外滩', 'username': '李四', 'title': '外滩夜游最佳体验', 'content': '建议傍晚5点到，先看日落再等亮灯。7点左右陆家嘴亮灯的瞬间特别震撼。可以坐2块钱的轮渡从外滩到陆家嘴，性价比超高的"黄浦江游船"。和平饭店门口拍照很有老上海的感觉。', 'tip_type': '实用建议', 'likes': 39},

        # 大熊猫基地
        {'spot': '大熊猫繁育研究基地', 'username': '小红', 'title': '看熊猫的最佳时间', 'content': '一定要早上去！8:30开门就冲进去，上午熊猫比较活跃，会爬树玩耍。下午基本都在睡觉，只能看到一团团黑色白色趴在树上。月亮产房和太阳产房可以看到熊猫宝宝，萌到爆炸。', 'tip_type': '实用建议', 'likes': 76},
        {'spot': '大熊猫繁育研究基地', 'username': '小明', 'title': '不要买门口的熊猫周边', 'content': '景区门口小贩卖的熊猫玩偶比里面贵一倍，而且质量差。园区内的纪念品商店价格更合理，款式也多。另外景区很大，建议坐观光车（10元），不然走路要很久。', 'tip_type': '避坑指南', 'likes': 34},

        # 西安城墙
        {'spot': '西安城墙', 'username': '王五', 'title': '城墙骑行攻略', 'content': '城墙全长13.7公里，骑一圈大概1.5小时。租车在南门（永宁门）最方便，单人车40元/2小时。建议下午4-5点开始骑，可以看到日落和华灯初上的城市。南门到东门这段风景最好。', 'tip_type': '实用建议', 'likes': 41},

        # 广州塔
        {'spot': '广州塔', 'username': '赵六', 'title': '广州塔省钱攻略', 'content': '广州塔门票分好几档，150元到398元不等。其实买150元的就够了，可以到108层观光层。最贵的包含摩天轮和跳楼机，胆小的没必要。建议傍晚上去，可以同时看到日景和夜景。塔下的珠江夜游也很值得，80块钱坐船一小时。', 'tip_type': '实用建议', 'likes': 29},

        # 磁器口
        {'spot': '磁器口古镇', 'username': '王五', 'title': '磁器口美食地图', 'content': '陈麻花是磁器口必买，但要认准"陈昌银"这个牌子，其他都是山寨的。毛血旺和鸡杂是磁器口特色，推荐"古镇鸡杂"这家店。手工酸辣粉也很好吃，5块钱一碗。周末人超多，建议工作日去。', 'tip_type': '美食推荐', 'likes': 48},

        # 宽窄巷子
        {'spot': '宽窄巷子', 'username': '小明', 'title': '宽窄巷子怎么逛', 'content': '宽窄巷子分三条街：宽巷子、窄巷子、井巷子。宽巷子最热闹，茶馆和小吃多；窄巷子文艺一些，有特色小店；井巷子最安静，有创意墙绘。建议花2小时慢慢逛。三大炮和糖油果子是必吃小吃。掏耳朵30元可以体验一下。', 'tip_type': '实用建议', 'likes': 37},

        # 颐和园
        {'spot': '颐和园', 'username': '李四', 'title': '颐和园半天游路线', 'content': '时间紧的话走这条线：东宫门进→仁寿殿→长廊（728米，世界最长画廊）→排云殿→佛香阁（俯瞰昆明湖绝佳）→石舫→苏州街→北宫门出。全程约3小时。佛香阁要爬很多台阶，但景色绝对值得。', 'tip_type': '实用建议', 'likes': 52},

        # 长隆
        {'spot': '长隆野生动物世界', 'username': '小红', 'title': '长隆亲子攻略', 'content': '带小朋友去长隆一定要做好一天的准备，园区超大。上午先坐小火车看散养动物（人少），下午看表演和逛步行区。自驾车游览区可以近距离看长颈鹿和斑马，小朋友超兴奋。里面的饭又贵又难吃，建议自带零食。', 'tip_type': '实用建议', 'likes': 61},
    ]

    created = 0
    for data in tips_data:
        try:
            spot = Spot.objects.get(name=data['spot'])
            user = User.objects.get(username=data['username'])
            tip = SpotTip.objects.create(
                spot=spot,
                user=user,
                title=data['title'],
                content=data['content'],
                tip_type=data['tip_type'],
                likes=data['likes'],
            )
            created += 1
            print(f"  ✅ [{data['spot']}] {data['title']}")
        except Spot.DoesNotExist:
            print(f"  ❌ 景点不存在: {data['spot']}")
        except User.DoesNotExist:
            print(f"  ❌ 用户不存在: {data['username']}")

    print(f"\n攻略创建完成，共 {created} 篇\n")


if __name__ == "__main__":
    print("=" * 50)
    print("开始导入景点攻略...")
    print("=" * 50)
    load_tips()
    print("全部完成！")
