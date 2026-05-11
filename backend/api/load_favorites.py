import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from backend.api.models import Spot, Favorite


def create_favorites():
    """
    根据用户的旅行日记和兴趣偏好，生成收藏数据
    设计逻辑：
    - 每个用户收藏 8~12 个景点（跨多个城市）
    - 收藏偏好与日记内容一致（去过且喜欢的景点会收藏）
    - 部分收藏体现"想去但还没去"的探索性
    """
    # 清除旧收藏
    Favorite.objects.all().delete()
    print("已清除旧收藏数据")

    # 收藏数据：用户名 → 收藏的景点名列表
    # 设计依据参考各用户的旅行日记内容
    favorites_map = {
        # 李四：偏好历史文化和自然风光，去过北京/成都/上海
        '李四': [
            '故宫博物院',      # 日记："太震撼了"，五星好评
            '天坛公园',        # 历史文化爱好者必收
            '颐和园',          # 皇家园林，符合偏好
            '大熊猫繁育研究基地',  # 成都行最爱
            '武侯祠',          # 三国文化
            '外滩',            # 上海地标
            '西湖',            # 还没去过，想去
            '秦始皇兵马俑博物馆',  # 还没去过，计划中
        ],

        # 王五：偏好历史古迹和自然景观，去过西安/重庆/杭州
        '王五': [
            '秦始皇兵马俑博物馆',  # 日记："震撼到说不出话"
            '西安城墙',         # 骑自行车绕城
            '陕西历史博物馆',    # "唐三彩太精美了"
            '洪崖洞',          # "像千与千寻"
            '武隆天生三桥',     # 自然景观爱好者
            '西湖',           # "百去不厌"
            '灵隐寺',          # 杭州行打卡
            '故宫博物院',       # 还没去过，想去
            '青城山',          # 还没去过，喜欢登山
        ],

        # 赵六：偏好美食和城市体验，去过广州/北京
        '赵六': [
            '广州塔',          # 日记："登顶，腿都软了"
            '陈家祠',          # 岭南建筑
            '沙面岛',          # 拍照打卡
            '珠江夜游',        # 夜景浪漫
            '八达岭长城',       # "好汉打卡"
            '锦里',           # 还没去过，美食街
            '宽窄巷子',        # 还没去过，想去
            '外滩',           # 还没去过
        ],

        # 小明：偏好文化和深度体验，一个人旅行，去过西安/上海
        '小明': [
            '西安城墙',        # 日记："夕阳把砖墙染成金色"
            '碑林博物馆',       # "古老的石碑让人感动"
            '大唐芙蓉园',       # 唐文化体验
            '上海迪士尼',       # "大人也要有童话"
            '武康路',          # 上海文艺路线
            '798艺术区',       # 还没去过，艺术爱好者
            '故宫博物院',       # 还没去过
            '杜甫草堂',        # 还没去过，文化气息
            '龙井村',          # 还没去过，想体验
        ],

        # 小红：偏好自然和休闲，和闺蜜出行，去过成都/广州/杭州
        '小红': [
            '大熊猫繁育研究基地',  # 日记："尖叫了，太可爱！"
            '都江堰',          # "佩服古人的智慧"
            '青城山',          # "空气清新到想住下"
            '人民公园',         # 喝茶慢生活
            '长隆野生动物世界',   # 广州行最爱
            '九溪烟树',         # "红叶美得像油画"
            '西湖',           # 杭州经典
            '西溪湿地',         # 休闲放松
            '沙面岛',          # 拍照打卡
            '豫园',           # 还没去过，想去
        ],
    }

    created = 0
    for username, spot_names in favorites_map.items():
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            print(f"  ❌ 用户 {username} 不存在，跳过")
            continue

        for spot_name in spot_names:
            try:
                spot = Spot.objects.get(name=spot_name)
                fav, is_new = Favorite.objects.get_or_create(user=user, spot=spot)
                if is_new:
                    created += 1
                    print(f"  ✅ [{username}] 收藏了 {spot.name}")
                else:
                    print(f"  ⏭️  [{username}] 已收藏 {spot.name}")
            except Spot.DoesNotExist:
                print(f"  ❌ 景点 {spot_name} 不存在，跳过")

    print(f"\n收藏数据创建完成，共 {created} 条\n")


if __name__ == "__main__":
    print("=" * 50)
    print("开始创建收藏数据...")
    print("=" * 50)
    create_favorites()
    print("完成！")
