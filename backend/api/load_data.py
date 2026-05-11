import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.api.models import Spot

def load_initial_data():
    spots_data = [
        # ======================= 北京 (15个) =======================
        {"name": "故宫博物院", "city": "北京", "address": "北京市东城区景山前街4号", "price": 60, "duration": 4.0, "longitude": 116.397, "latitude": 39.917, "tags": "历史,文化,世界遗产", "rating": 5.0, "description": "世界五大宫之首，明清两代的皇家宫殿。"},
        {"name": "天坛公园", "city": "北京", "address": "北京市东城区天坛东里甲1号", "price": 34, "duration": 2.5, "longitude": 116.410, "latitude": 39.882, "tags": "历史,园林,建筑", "rating": 4.8, "description": "明清两代皇帝祭天、祈谷的场所。"},
        {"name": "颐和园", "city": "北京", "address": "北京市海淀区新建宫门路19号", "price": 30, "duration": 4.0, "longitude": 116.273, "latitude": 39.993, "tags": "历史,园林,亲子", "rating": 4.9, "description": "保存最完整的一座皇家行宫御苑，被誉为皇家园林博物馆。"},
        {"name": "八达岭长城", "city": "北京", "address": "北京市延庆区G6京藏高速58号出口", "price": 40, "duration": 5.0, "longitude": 116.011, "latitude": 40.359, "tags": "历史,文化,自然", "rating": 4.7, "description": "不到长城非好汉，明长城向游人开放最早的地段。"},
        {"name": "圆明园", "city": "北京", "address": "北京市海淀区清华西路28号", "price": 25, "duration": 3.0, "longitude": 116.304, "latitude": 40.008, "tags": "历史,园林,爱国教育", "rating": 4.6, "description": "清代大型皇家园林，曾被誉为万园之园。"},
        {"name": "恭王府", "city": "北京", "address": "北京市西城区前海西街17号", "price": 40, "duration": 2.0, "longitude": 116.386, "latitude": 39.937, "tags": "历史,文化,建筑", "rating": 4.8, "description": "一座恭王府，半部清代史，和珅的旧居。"},
        {"name": "南锣鼓巷", "city": "北京", "address": "北京市东城区南锣鼓巷", "price": 0, "duration": 2.0, "longitude": 116.403, "latitude": 39.938, "tags": "文化,现代,网红打卡", "rating": 4.5, "description": "北京最古老的街区之一，充满老北京风情和现代文艺气息。"},
        {"name": "雍和宫", "city": "北京", "address": "北京市东城区雍和宫大街12号", "price": 25, "duration": 2.0, "longitude": 116.417, "latitude": 39.947, "tags": "历史,文化,宗教", "rating": 4.9, "description": "北京市内最大的藏传佛教寺院。"},
        {"name": "景山公园", "city": "北京", "address": "北京市西城区景山西街44号", "price": 2, "duration": 1.5, "longitude": 116.397, "latitude": 39.925, "tags": "园林,历史,夜景", "rating": 4.7, "description": "可以俯瞰故宫全景的绝佳地点。"},
        {"name": "中国国家博物馆", "city": "北京", "address": "北京市东城区东长安街16号", "price": 0, "duration": 4.0, "longitude": 116.403, "latitude": 39.904, "tags": "历史,文化,亲子,展览", "rating": 5.0, "description": "集中反映中华优秀传统文化的国家最高历史文化艺术殿堂。"},
        {"name": "鸟巢(国家体育场)", "city": "北京", "address": "北京市朝阳区国家体育场南路1号", "price": 50, "duration": 1.5, "longitude": 116.396, "latitude": 39.990, "tags": "现代,建筑,亲子", "rating": 4.6, "description": "2008年北京奥运会主体育场。"},
        {"name": "水立方", "city": "北京", "address": "北京市朝阳区天辰东路11号", "price": 30, "duration": 1.5, "longitude": 116.384, "latitude": 39.990, "tags": "现代,建筑,亲子", "rating": 4.6, "description": "2008年北京奥运会标志性建筑物之一。"},
        {"name": "北京环球度假区", "city": "北京", "address": "北京市通州区环球大道1号", "price": 528, "duration": 8.0, "longitude": 116.671, "latitude": 39.802, "tags": "现代,亲子,主题乐园", "rating": 4.8, "description": "亚洲第三座、世界第五座环球主题公园。"},
        {"name": "什刹海", "city": "北京", "address": "北京市西城区地安门西大街49号", "price": 0, "duration": 2.0, "longitude": 116.387, "latitude": 39.938, "tags": "历史,文化,夜景,休闲", "rating": 4.7, "description": "北京内城唯一一处具有开阔水面的开放型景区。"},
        {"name": "798艺术区", "city": "北京", "address": "北京市朝阳区酒仙桥路4号", "price": 0, "duration": 3.0, "longitude": 116.497, "latitude": 39.984, "tags": "现代,文化,艺术,网红打卡", "rating": 4.5, "description": "北京都市文化的新地标，充满现代艺术气息。"},

        # ======================= 上海 (15个) =======================
        {"name": "外滩", "city": "上海", "address": "上海市黄浦区中山东一路", "price": 0, "duration": 1.5, "longitude": 121.488, "latitude": 31.233, "tags": "历史,现代,夜景,建筑", "rating": 5.0, "description": "上海的地标，隔江相望陆家嘴金融中心。"},
        {"name": "东方明珠", "city": "上海", "address": "上海市浦东新区世纪大道1号", "price": 199, "duration": 2.5, "longitude": 121.499, "latitude": 31.239, "tags": "现代,建筑,亲子,夜景", "rating": 4.8, "description": "上海标志性文化景观之一，俯瞰浦江两岸。"},
        {"name": "上海迪士尼度假区", "city": "上海", "address": "上海市浦东新区黄赵路310号", "price": 475, "duration": 8.0, "longitude": 121.667, "latitude": 31.141, "tags": "现代,亲子,主题乐园", "rating": 4.9, "description": "中国大陆首座迪士尼主题乐园，点亮心中奇梦。"},
        {"name": "豫园", "city": "上海", "address": "上海市黄浦区福佑路168号", "price": 40, "duration": 2.0, "longitude": 121.492, "latitude": 31.227, "tags": "历史,园林,文化", "rating": 4.6, "description": "江南古典园林，著名的城隍庙就在旁边。"},
        {"name": "南京路步行街", "city": "上海", "address": "上海市黄浦区南京东路", "price": 0, "duration": 2.0, "longitude": 121.474, "latitude": 31.234, "tags": "现代,购物,夜景", "rating": 4.7, "description": "中华商业第一街，十里洋场的繁华见证。"},
        {"name": "田子坊", "city": "上海", "address": "上海市黄浦区泰康路210弄", "price": 0, "duration": 2.0, "longitude": 121.469, "latitude": 31.208, "tags": "文化,艺术,现代,小资", "rating": 4.4, "description": "充满里弄风情与文艺气息的创意产业聚集区。"},
        {"name": "上海中心大厦", "city": "上海", "address": "上海市浦东新区银城中路501号", "price": 180, "duration": 2.0, "longitude": 121.505, "latitude": 31.233, "tags": "现代,建筑,夜景", "rating": 4.8, "description": "中国第一高楼，可鸟瞰整个上海滩。"},
        {"name": "上海博物馆", "city": "上海", "address": "上海市黄浦区人民大道201号", "price": 0, "duration": 3.0, "longitude": 121.475, "latitude": 31.228, "tags": "历史,文化,亲子,展览", "rating": 4.9, "description": "馆藏珍贵文物14万件，特别是青铜器闻名中外。"},
        {"name": "新天地", "city": "上海", "address": "上海市黄浦区太仓路181弄", "price": 0, "duration": 2.0, "longitude": 121.475, "latitude": 31.222, "tags": "历史,现代,休闲,小资", "rating": 4.5, "description": "以上海近代建筑标志石库门建筑旧区为基础改造的休闲步行街。"},
        {"name": "中华艺术宫", "city": "上海", "address": "上海市浦东新区上南路205号", "price": 0, "duration": 3.0, "longitude": 121.499, "latitude": 31.185, "tags": "文化,艺术,现代,展览", "rating": 4.6, "description": "前身是世博会中国国家馆，现为极具特色的美术馆。"},
        {"name": "陆家嘴", "city": "上海", "address": "上海市浦东新区", "price": 0, "duration": 2.0, "longitude": 121.501, "latitude": 31.236, "tags": "现代,金融,夜景", "rating": 4.8, "description": "中国最具影响力的金融中心，高楼林立。"},
        {"name": "朱家角古镇", "city": "上海", "address": "上海市青浦区课植园路555号", "price": 0, "duration": 4.0, "longitude": 121.050, "latitude": 31.111, "tags": "历史,文化,水乡", "rating": 4.5, "description": "上海威尼斯，典型的江南水乡古镇。"},
        {"name": "世纪公园", "city": "上海", "address": "上海市浦东新区锦绣路1001号", "price": 10, "duration": 2.5, "longitude": 121.551, "latitude": 31.218, "tags": "园林,亲子,休闲,自然", "rating": 4.6, "description": "上海内环线中心区域内最大的富有自然特征的生态型城市公园。"},
        {"name": "上海科技馆", "city": "上海", "address": "上海市浦东新区世纪大道2000号", "price": 45, "duration": 4.0, "longitude": 121.542, "latitude": 31.218, "tags": "科普,亲子,现代,展览", "rating": 4.7, "description": "以自然、人、科技为主题的大型科普教育基地。"},
        {"name": "武康路", "city": "上海", "address": "上海市徐汇区武康路", "price": 0, "duration": 1.5, "longitude": 121.442, "latitude": 31.205, "tags": "历史,文化,小资,网红打卡", "rating": 4.6, "description": "浓缩了上海近百年历史的名人路，洋房林立。"},

        # ======================= 成都 (12个) =======================
        {"name": "大熊猫繁育研究基地", "city": "成都", "address": "成都市成华区熊猫大道1375号", "price": 55, "duration": 4.0, "longitude": 104.142, "latitude": 30.732, "tags": "亲子,自然,动物", "rating": 5.0, "description": "看国宝大熊猫的首选之地。"},
        {"name": "宽窄巷子", "city": "成都", "address": "成都市青羊区长顺街附近", "price": 0, "duration": 2.0, "longitude": 104.053, "latitude": 30.663, "tags": "历史,文化,网红打卡", "rating": 4.6, "description": "成都遗留下来的较成规模的清朝古街道。"},
        {"name": "锦里", "city": "成都", "address": "成都市武侯区武侯祠大街231号附1号", "price": 0, "duration": 2.0, "longitude": 104.048, "latitude": 30.645, "tags": "历史,文化,夜景,美食", "rating": 4.7, "description": "西蜀第一街，体验三国文化与成都民俗的绝佳去处。"},
        {"name": "武侯祠", "city": "成都", "address": "成都市武侯区武侯祠大街231号", "price": 50, "duration": 2.0, "longitude": 104.048, "latitude": 30.645, "tags": "历史,文化", "rating": 4.8, "description": "中国唯一的君臣合祀祠庙，三国文化胜地。"},
        {"name": "杜甫草堂", "city": "成都", "address": "成都市青羊区青华路37号", "price": 50, "duration": 2.0, "longitude": 104.028, "latitude": 30.660, "tags": "历史,文化,园林", "rating": 4.7, "description": "唐代大诗人杜甫流寓成都时的故居。"},
        {"name": "青城山", "city": "成都", "address": "成都市都江堰市青城山路", "price": 80, "duration": 5.0, "longitude": 103.567, "latitude": 30.900, "tags": "自然,历史,宗教,登山", "rating": 4.8, "description": "青城天下幽，中国道教发源地之一。"},
        {"name": "都江堰", "city": "成都", "address": "成都市都江堰市公园路", "price": 80, "duration": 4.0, "longitude": 103.612, "latitude": 31.001, "tags": "历史,文化,水利,自然", "rating": 4.9, "description": "造福千秋的伟大水利工程。"},
        {"name": "春熙路", "city": "成都", "address": "成都市锦江区春熙路", "price": 0, "duration": 2.0, "longitude": 104.078, "latitude": 30.655, "tags": "现代,购物,网红打卡", "rating": 4.6, "description": "成都最繁华的商业步行街。"},
        {"name": "金沙遗址博物馆", "city": "成都", "address": "成都市青羊区金沙遗址路2号", "price": 70, "duration": 3.0, "longitude": 104.011, "latitude": 30.684, "tags": "历史,文化,展览", "rating": 4.8, "description": "展示神秘古蜀文明的重要遗址。"},
        {"name": "人民公园", "city": "成都", "address": "成都市青羊区少城路12号", "price": 0, "duration": 1.5, "longitude": 104.056, "latitude": 30.657, "tags": "休闲,园林,文化,现代", "rating": 4.5, "description": "体验成都人喝茶打牌慢生活的最佳地点鹤鸣茶社所在地。"},
        {"name": "文殊院", "city": "成都", "address": "成都市青羊区文殊院街66号", "price": 0, "duration": 1.5, "longitude": 104.068, "latitude": 30.675, "tags": "历史,文化,宗教", "rating": 4.6, "description": "川西著名佛教寺院，清净安详。"},
        {"name": "九眼桥", "city": "成都", "address": "成都市锦江区九眼桥", "price": 0, "duration": 2.0, "longitude": 104.088, "latitude": 30.640, "tags": "夜景,休闲,现代,酒吧", "rating": 4.5, "description": "成都夜生活的标志性地点。"},

        # ======================= 西安 (10个) =======================
        {"name": "秦始皇兵马俑博物馆", "city": "西安", "address": "西安市临潼区秦陵北路", "price": 120, "duration": 4.0, "longitude": 109.278, "latitude": 34.384, "tags": "历史,文化,世界遗产", "rating": 5.0, "description": "世界第八大奇迹，气势磅礴的地下军阵。"},
        {"name": "大雁塔", "city": "西安", "address": "西安市雁塔区慈恩路1号", "price": 40, "duration": 2.0, "longitude": 108.959, "latitude": 34.218, "tags": "历史,文化,宗教", "rating": 4.8, "description": "唐玄奘保存经书的佛塔，西安的地标。"},
        {"name": "西安城墙", "city": "西安", "address": "西安市碑林区南门", "price": 54, "duration": 3.0, "longitude": 108.947, "latitude": 34.254, "tags": "历史,文化,骑行,夜景", "rating": 4.7, "description": "中国现存规模最大、保存最完整的古代城垣。"},
        {"name": "钟楼", "city": "西安", "address": "西安市碑林区东西南北四条大街交汇处", "price": 30, "duration": 1.0, "longitude": 108.946, "latitude": 34.261, "tags": "历史,文化,夜景,建筑", "rating": 4.6, "description": "西安市中心的地标，夜景尤其辉煌。"},
        {"name": "回民街", "city": "西安", "address": "西安市莲湖区北院门", "price": 0, "duration": 2.0, "longitude": 108.941, "latitude": 34.264, "tags": "文化,美食,夜景,网红打卡", "rating": 4.5, "description": "著名的美食文化街区，吃货的天堂。"},
        {"name": "华清宫", "city": "西安", "address": "西安市临潼区华清路38号", "price": 120, "duration": 3.0, "longitude": 109.213, "latitude": 34.364, "tags": "历史,园林,温泉", "rating": 4.6, "description": "唐明皇与杨贵妃的爱情发生地。"},
        {"name": "陕西历史博物馆", "city": "西安", "address": "西安市雁塔区小寨东路91号", "price": 0, "duration": 4.0, "longitude": 108.953, "latitude": 34.225, "tags": "历史,文化,展览", "rating": 4.9, "description": "古都明珠，华夏宝库，一票难求的国家级博物馆。"},
        {"name": "大唐芙蓉园", "city": "西安", "address": "西安市雁塔区芙蓉西路99号", "price": 120, "duration": 3.0, "longitude": 108.966, "latitude": 34.212, "tags": "历史,园林,夜景,亲子", "rating": 4.6, "description": "展示盛唐风貌的大型皇家园林式文化主题公园。"},
        {"name": "小雁塔", "city": "西安", "address": "西安市碑林区友谊西路72号", "price": 0, "duration": 2.0, "longitude": 108.939, "latitude": 34.240, "tags": "历史,文化,园林,宗教", "rating": 4.5, "description": "唐代长安城保留至今的重要标志。"},
        {"name": "大明宫国家遗址公园", "city": "西安", "address": "西安市新城区自强东路585号", "price": 60, "duration": 3.0, "longitude": 108.959, "latitude": 34.288, "tags": "历史,文化,遗址,公园", "rating": 4.5, "description": "盛唐时期的大朝正殿，规模极其宏大。"},

        # ======================= 杭州 (10个) =======================
        {"name": "西湖", "city": "杭州", "address": "杭州市西湖区龙井路1号", "price": 0, "duration": 4.0, "longitude": 120.148, "latitude": 30.242, "tags": "历史,文化,自然,园林", "rating": 5.0, "description": "欲把西湖比西子，淡妆浓抹总相宜。世界文化遗产。"},
        {"name": "灵隐寺", "city": "杭州", "address": "杭州市西湖区法云弄1号", "price": 75, "duration": 3.0, "longitude": 120.100, "latitude": 30.250, "tags": "历史,文化,宗教", "rating": 4.8, "description": "江南著名古刹，香火鼎盛。"},
        {"name": "千岛湖", "city": "杭州", "address": "杭州市淳安县千岛湖镇", "price": 150, "duration": 6.0, "longitude": 119.028, "latitude": 29.608, "tags": "自然,亲子,休闲", "rating": 4.7, "description": "天下第一秀水，1078个岛屿星罗棋布。"},
        {"name": "宋城", "city": "杭州", "address": "杭州市西湖区之江路148号", "price": 290, "duration": 4.0, "longitude": 120.086, "latitude": 30.172, "tags": "历史,文化,亲子,演出", "rating": 4.6, "description": "给我一天，还你千年。大型宋文化主题公园。"},
        {"name": "西溪湿地", "city": "杭州", "address": "杭州市西湖区天目山路518号", "price": 80, "duration": 3.0, "longitude": 120.068, "latitude": 30.262, "tags": "自然,休闲,亲子", "rating": 4.6, "description": "城市中的天然氧吧，非诚勿扰拍摄地。"},
        {"name": "龙井村", "city": "杭州", "address": "杭州市西湖区龙井村", "price": 0, "duration": 2.0, "longitude": 120.112, "latitude": 30.228, "tags": "文化,休闲,美食", "rating": 4.5, "description": "问茶龙井村，品一杯明前龙井。"},
        {"name": "河坊街", "city": "杭州", "address": "杭州市上城区河坊街", "price": 0, "duration": 2.0, "longitude": 120.169, "latitude": 30.244, "tags": "历史,文化,美食,购物", "rating": 4.5, "description": "杭州最具代表性的历史文化街区。"},
        {"name": "九溪烟树", "city": "杭州", "address": "杭州市西湖区龙井村九溪", "price": 0, "duration": 2.5, "longitude": 120.115, "latitude": 30.215, "tags": "自然,休闲,网红打卡", "rating": 4.7, "description": "九溪十八涧，山中最胜处。徒步爱好者天堂。"},
        {"name": "钱塘江大桥", "city": "杭州", "address": "杭州市滨江区", "price": 0, "duration": 1.0, "longitude": 120.143, "latitude": 30.208, "tags": "历史,建筑,夜景", "rating": 4.4, "description": "中国自行设计建造的第一座公铁两用桥。"},
        {"name": "南宋御街", "city": "杭州", "address": "杭州市上城区中山中路", "price": 0, "duration": 1.5, "longitude": 120.170, "latitude": 30.250, "tags": "历史,文化,购物", "rating": 4.5, "description": "南宋都城的中轴线，再现千年繁华。"},

        # ======================= 重庆 (10个) =======================
        {"name": "洪崖洞", "city": "重庆", "address": "重庆市渝中区嘉陵江滨江路88号", "price": 0, "duration": 2.0, "longitude": 106.574, "latitude": 29.563, "tags": "现代,夜景,网红打卡,建筑", "rating": 4.8, "description": "现实版千与千寻，重庆最具代表性的夜景地标。"},
        {"name": "磁器口古镇", "city": "重庆", "address": "重庆市沙坪坝区磁器口", "price": 0, "duration": 3.0, "longitude": 106.456, "latitude": 29.523, "tags": "历史,文化,美食", "rating": 4.5, "description": "一条石板路，千年磁器口。重庆古城的缩影。"},
        {"name": "长江索道", "city": "重庆", "address": "重庆市渝中区新华路151号", "price": 20, "duration": 0.5, "longitude": 106.572, "latitude": 29.556, "tags": "现代,体验,夜景,网红打卡", "rating": 4.6, "description": "山城空中巴士，飞越长江的独特体验。"},
        {"name": "解放碑", "city": "重庆", "address": "重庆市渝中区解放碑", "price": 0, "duration": 1.5, "longitude": 106.571, "latitude": 29.559, "tags": "历史,现代,购物,夜景", "rating": 4.5, "description": "重庆的城市名片，西部第一条商业步行街。"},
        {"name": "武隆天生三桥", "city": "重庆", "address": "重庆市武隆区仙女山镇", "price": 125, "duration": 4.0, "longitude": 107.805, "latitude": 29.426, "tags": "自然,世界遗产,亲子", "rating": 4.9, "description": "世界最大天生桥群，变形金刚4取景地。"},
        {"name": "李子坝轻轨站", "city": "重庆", "address": "重庆市渝中区李子坝", "price": 0, "duration": 0.5, "longitude": 106.551, "latitude": 29.553, "tags": "现代,网红打卡,建筑", "rating": 4.5, "description": "轻轨穿楼而过，重庆魔幻交通的代表。"},
        {"name": "南山一棵树", "city": "重庆", "address": "重庆市南岸区南山", "price": 30, "duration": 1.5, "longitude": 106.605, "latitude": 29.537, "tags": "夜景,休闲,网红打卡", "rating": 4.6, "description": "俯瞰重庆夜景的最佳观景台。"},
        {"name": "大足石刻", "city": "重庆", "address": "重庆市大足区", "price": 115, "duration": 4.0, "longitude": 105.720, "latitude": 29.707, "tags": "历史,文化,世界遗产", "rating": 4.9, "description": "世界石窟艺术最后的丰碑。"},
        {"name": "朝天门", "city": "重庆", "address": "重庆市渝中区朝天门", "price": 0, "duration": 1.0, "longitude": 106.585, "latitude": 29.568, "tags": "历史,文化,夜景", "rating": 4.4, "description": "两江交汇处，重庆最古老的城门。"},
        {"name": "鹅岭二厂", "city": "重庆", "address": "重庆市渝中区鹅岭正街1号", "price": 0, "duration": 2.0, "longitude": 106.551, "latitude": 29.550, "tags": "文化,艺术,网红打卡,现代", "rating": 4.5, "description": "从你的全世界路过取景地，文艺青年打卡圣地。"},

        # ======================= 广州 (10个) =======================
        {"name": "广州塔", "city": "广州", "address": "广州市海珠区阅江西路222号", "price": 150, "duration": 2.5, "longitude": 113.324, "latitude": 23.106, "tags": "现代,建筑,夜景,网红打卡", "rating": 4.8, "description": "小蛮腰，中国第一高塔，广州地标。"},
        {"name": "陈家祠", "city": "广州", "address": "广州市荔湾区中山七路恩龙里34号", "price": 10, "duration": 2.0, "longitude": 113.247, "latitude": 23.128, "tags": "历史,文化,建筑", "rating": 4.7, "description": "岭南建筑艺术的集大成者，广东民间工艺博物馆。"},
        {"name": "沙面岛", "city": "广州", "address": "广州市荔湾区沙面", "price": 0, "duration": 2.0, "longitude": 113.236, "latitude": 23.110, "tags": "历史,文化,建筑,网红打卡", "rating": 4.6, "description": "欧陆风情小岛，广州最有异国情调的地方。"},
        {"name": "白云山", "city": "广州", "address": "广州市白云区广园中路", "price": 5, "duration": 4.0, "longitude": 113.298, "latitude": 23.191, "tags": "自然,休闲,登山", "rating": 4.5, "description": "羊城第一秀，广州的绿肺。"},
        {"name": "长隆野生动物世界", "city": "广州", "address": "广州市番禺区大石镇", "price": 300, "duration": 6.0, "longitude": 113.309, "latitude": 23.002, "tags": "亲子,自然,动物", "rating": 4.9, "description": "中国最具国际水准的野生动物园。"},
        {"name": "北京路步行街", "city": "广州", "address": "广州市越秀区北京路", "price": 0, "duration": 2.0, "longitude": 113.268, "latitude": 23.129, "tags": "历史,现代,购物,美食", "rating": 4.5, "description": "广州最繁华的商业街，千年古道遗址。"},
        {"name": "越秀公园", "city": "广州", "address": "广州市越秀区解放北路988号", "price": 0, "duration": 2.0, "longitude": 113.265, "latitude": 23.139, "tags": "历史,自然,园林", "rating": 4.4, "description": "广州最大的综合性公园，五羊雕像所在地。"},
        {"name": "珠江夜游", "city": "广州", "address": "广州市沿江路天字码头", "price": 80, "duration": 1.5, "longitude": 113.268, "latitude": 23.116, "tags": "夜景,休闲,浪漫", "rating": 4.7, "description": "夜游珠江，感受广州两岸璀璨灯火。"},
        {"name": "广州博物馆(镇海楼)", "city": "广州", "address": "广州市越秀区解放北路988号", "price": 10, "duration": 1.5, "longitude": 113.264, "latitude": 23.140, "tags": "历史,文化,展览", "rating": 4.4, "description": "广州标志性古建筑，馆藏广州历史文物。"},
        {"name": "红砖厂创意园", "city": "广州", "address": "广州市天河区员村四横路128号", "price": 0, "duration": 2.0, "longitude": 113.352, "latitude": 23.119, "tags": "现代,艺术,网红打卡", "rating": 4.5, "description": "广州的798，由旧厂房改造的创意艺术区。"},
    ]

    print(f"即将清除旧数据并导入 {len(spots_data)} 条新景点数据...")
    
    Spot.objects.all().delete()
    
    count = 0
    for data in spots_data:
        data['image_url'] = f"https://picsum.photos/seed/{data['name']}/400/300"
        Spot.objects.create(**data)
        count += 1
        
    print(f"导入成功！共写入了 {count} 条景点数据。")

if __name__ == "__main__":
    load_initial_data()
