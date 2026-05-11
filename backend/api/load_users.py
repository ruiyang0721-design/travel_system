import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from backend.api.models import TravelDiary


def create_users():
    """创建测试用户"""
    users_data = [
        {'username': '李四', 'email': 'lisi@test.com'},
        {'username': '王五', 'email': 'wangwu@test.com'},
        {'username': '赵六', 'email': 'zhaoliu@test.com'},
        {'username': '小明', 'email': 'xiaoming@test.com'},
        {'username': '小红', 'email': 'xiaohong@test.com'},
    ]

    password = make_password('123456789')
    created = 0
    for data in users_data:
        user, is_new = User.objects.get_or_create(
            username=data['username'],
            defaults={'email': data['email'], 'password': password}
        )
        if is_new:
            created += 1
            print(f"  ✅ 创建用户: {data['username']}")
        else:
            print(f"  ⏭️  用户已存在: {data['username']}")

    print(f"\n用户处理完成，新创建 {created} 个\n")


def create_diaries():
    """创建旅行日记"""
    # 清除旧日记
    TravelDiary.objects.all().delete()
    print("已清除旧日记数据")

    diaries_data = [
        # 李四的日记
        {
            'username': '李四',
            'title': '故宫一日游，穿越回明清',
            'city': '北京',
            'content': '今天终于去了心心念念的故宫！从午门进去，沿着中轴线一路走到神武门，三大殿的气势真的太震撼了。建议大家一定要早点去，八点半开门就进，人少拍照特别好。珍宝馆和钟表馆额外收费但绝对值得，那些精致的工艺品让人叹为观止。在御花园里坐了一会儿，想象当年皇帝在这里散步的样子。出来后去了景山公园俯瞰故宫全景，夕阳下的紫禁城美得像一幅画。一天走了两万多步，腿都快断了，但真的不虚此行！',
            'rating': 5,
        },
        {
            'username': '李四',
            'title': '成都三天两夜，巴适得板',
            'city': '成都',
            'content': '成都真的是一个来了就不想走的城市。第一天去了宽窄巷子和锦里，边逛边吃，钵钵鸡、蛋烘糕、三大炮，嘴巴就没停过。第二天一早去了大熊猫繁育基地，看到圆滚滚的熊猫宝宝在树上打滚，心都化了。下午去了武侯祠感受三国文化，晚上在九眼桥的酒吧街喝了几杯。第三天去了杜甫草堂，幽静的竹林和茅屋让人暂时忘掉了城市的喧嚣。成都的节奏真的很慢很舒服，下次还来！',
            'rating': 5,
        },
        {
            'username': '李四',
            'title': '上海外滩夜景，不愧是魔都',
            'city': '上海',
            'content': '出差顺便在上海玩了两天。外滩的夜景果然名不虚传，陆家嘴的高楼灯光倒映在黄浦江上，太美了。第二天去了豫园和城隍庙，小笼包真的好吃！南京路步行街逛了逛，人太多了。武康路很适合拍照，那些老洋房特别有味道。下次想多留几天去迪士尼。',
            'rating': 4,
        },

        # 王五的日记
        {
            'username': '王五',
            'title': '西安三日行，梦回大唐',
            'city': '西安',
            'content': '西安是我去过的最有历史厚重感的城市！第一天去了兵马俑，站在一号坑前真的会被那种气势震撼到说不出话。导游讲解得很细致，每个俑的表情都不一样，太神奇了。第二天骑了城墙自行车，绕城一圈大概两个小时，城墙上视野特别好。晚上去回民街吃了羊肉泡馍和肉夹馍，味道绝了。第三天去了大雁塔和陕西历史博物馆，博物馆里的唐三彩和金银器太精美了。强烈推荐西安给所有喜欢历史的朋友！',
            'rating': 5,
        },
        {
            'username': '王五',
            'title': '重庆三天，被8D城市征服了',
            'city': '重庆',
            'content': '重庆真的太魔幻了！导航在这里完全失灵，明明显示目的地就在旁边，结果你在一楼它在十楼。洪崖洞的夜景真的像千与千寻，层层叠叠的灯光太梦幻了。坐了长江索道飞越长江，体验感拉满。去武隆看了天生三桥，变形金刚取景地果然壮观。吃了正宗的重庆火锅，微辣就已经辣到怀疑人生了，但停不下来。李子坝轻轨穿楼而过的瞬间，全车厢的人都在拍照哈哈。',
            'rating': 5,
        },
        {
            'username': '王五',
            'title': '杭州西湖，淡妆浓抹总相宜',
            'city': '杭州',
            'content': '西湖真的是百去不厌。这次是春天去的，苏堤两边的柳树刚发芽，桃花也开了，走在堤上感觉整个人都被治愈了。坐船去了三潭印月，湖面上微风拂过，舒服到不想走。下午去了灵隐寺，香火很旺，拜了拜祈了个平安。晚上在河坊街吃了东坡肉和龙井虾仁，杭帮菜清淡鲜美，很合我口味。第二天去了西溪湿地坐摇橹船，水乡的感觉特别悠闲。杭州真的是一个宜居又宜游的城市。',
            'rating': 5,
        },

        # 赵六的日记
        {
            'username': '赵六',
            'title': '广州美食之旅，吃到扶墙走',
            'city': '广州',
            'content': '去广州纯粹是为了吃！第一站就去了上下九步行街，肠粉、虾饺、烧卖、叉烧包，早茶吃到下午两点。陈家祠的岭南建筑太精美了，屋脊上的陶塑人物栩栩如生。沙面岛拍了很多照片，欧式建筑配上蓝天白云特别出片。晚上去珠江夜游，两岸的灯光倒映在水里很浪漫。第二天去了广州塔登顶，在塔顶的透明地板上往下看，腿都软了。白云山爬了半天，山顶的风景很值得。广州真的是吃货天堂，下次要带更大的胃来！',
            'rating': 5,
        },
        {
            'username': '赵六',
            'title': '长城好汉，八达岭打卡',
            'city': '北京',
            'content': '终于登上了长城！选了八达岭段，坐缆车上去再走下来的。站在城墙上远眺，蜿蜒的长城在群山间延伸，那种壮观真的无法用语言形容。爬到好汉坡的时候特别有成就感，拍照发了朋友圈收获了一百多个赞哈哈。下山后腿抖了三天，但真的值得。建议大家穿运动鞋，有些台阶真的很陡。冬天去的话人少很多，但要穿暖和。',
            'rating': 5,
        },

        # 小明的日记
        {
            'username': '小明',
            'title': '一个人的西安慢旅行',
            'city': '西安',
            'content': '一个人说走就走的旅行。没有做太多攻略，到了西安随便逛。第一天在城墙上骑了一圈自行车，傍晚的城墙特别美，夕阳把砖墙染成了金色。晚上去大唐不夜城走了走，灯火辉煌仿佛穿越回了盛唐。第二天在碑林博物馆待了一上午，那些古老的石碑上的字迹历经千年依然清晰，很感动。下午在回民街吃了一碗biangbiang面，真的好大一碗。旅行的意义就在于这种不期而遇的惊喜吧。',
            'rating': 4,
        },
        {
            'username': '小明',
            'title': '上海迪士尼，大人也要有童话',
            'city': '上海',
            'content': '谁说大人不能去迪士尼！一个人去的上海迪士尼，玩得比小朋友还开心。一进去就冲向创极速光轮，速度感太爽了。加勒比海盗的沉浸式体验做得太好了，坐了两次。花车巡游的时候看到米奇朝我挥手，莫名有点感动。晚上的烟花秀是整个旅程的高潮，城堡上的投影配上音乐和烟花，眼眶都湿了。虽然门票不便宜，但这种快乐是无价的。',
            'rating': 5,
        },

        # 小红的日记
        {
            'username': '小红',
            'title': '和闺蜜的成都之旅',
            'city': '成都',
            'content': '和闺蜜约了很久的成都之旅终于实现了！第一天直奔大熊猫基地，看到小熊猫的那一刻我俩尖叫了，太可爱了！下午在太古里逛街，成都的时尚感比我想象中强很多。晚上去吃了串串香，辣得我俩一直喝水但就是停不下来。第二天去了都江堰和青城山，都江堰的水利工程让人佩服古人的智慧，青城山的空气清新到想在这里住下。第三天在人民公园喝了一下午茶，看老大爷们打麻将，成都的慢生活真的太舒服了。',
            'rating': 5,
        },
        {
            'username': '小红',
            'title': '广州过年，花市和美食两不误',
            'city': '广州',
            'content': '春节去广州过年，感受了一把南方的年味。广州的迎春花市太热闹了，到处都是金桔和桃花，买了几束花带回酒店。年三十吃了顿正宗的粤式年夜饭，白切鸡、清蒸鱼、发菜蚝豉，每道菜都有好意头。初一去了沙面拍照，人不多很清净。初二逛了北京路步行街，千年古道遗址就在脚下，好神奇。初三去了长隆野生动物世界，看到了大熊猫和考拉。广州过年真的很有氛围，比北方热闹多了！',
            'rating': 5,
        },
        {
            'username': '小红',
            'title': '杭州秋日，满陇桂雨',
            'city': '杭州',
            'content': '秋天的杭州真的太香了！满觉陇的桂花开了整条街，空气里都是甜丝丝的桂花香。在龙井村喝了一杯新茶，茶农阿姨很热情地给我们讲怎么分辨龙井的好坏。九溪烟树的红叶美得像油画，溪水清澈见底。晚上在西湖边散步，断桥上人不多，月光洒在湖面上，突然就理解了为什么古人写那么多关于西湖的诗。杭州真的是一个四季都值得来的城市。',
            'rating': 5,
        },
    ]

    created = 0
    for data in diaries_data:
        try:
            user = User.objects.get(username=data['username'])
            diary = TravelDiary.objects.create(
                user=user,
                title=data['title'],
                city=data['city'],
                content=data['content'],
                
                rating=data['rating'],
            )
            created += 1
            print(f"  ✅ [{data['username']}] {data['title']}")
        except User.DoesNotExist:
            print(f"  ❌ 用户 {data['username']} 不存在，跳过")

    print(f"\n日记创建完成，共 {created} 篇\n")


if __name__ == "__main__":
    print("=" * 50)
    print("开始创建测试用户...")
    print("=" * 50)
    create_users()

    print("=" * 50)
    print("开始创建旅行日记...")
    print("=" * 50)
    create_diaries()

    print("全部完成！")
