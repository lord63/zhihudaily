### Github repo

* [GO-ZhihuDaily](https://github.com/Artwalk/GO-ZhihuDaily)
* [ZhihuDailyPurify-API](https://github.com/izzyleung/ZhihuDailyPurify/wiki/%E7%9F%A5%E4%B9%8E%E6%97%A5%E6%8A%A5-API-%E5%88%86%E6%9E%90)
* [zhihudaily by tornado on sae](https://github.com/JobsDong/zhihudaily)
* [zhihu.daily.rss](https://github.com/RicterZ/zhihu.daily.rss)

### zhihudaily web

* <http://zhihurewen.sinaapp.com/>
* <http://zhihudaily.ahorn.me/>
* <http://zhhrb.sinaapp.com>
* <http://zhihudaily.jd-app.com/>
* <http://www.kanzhihu.com/>
* <http://www.kanzhihu.com/>

### image url

* 新的 image url： <http://pic4.zhimg.com/87324b315fc1674451b56011ed5ead9d.jpg>
* 旧的 image url： <http://p4.zhimg.com/7e/b3/7eb3f89cf0f08ed9e9e5020ef2039bc3.jpg>

### Json 格式说明:

        {
            "date": "20150210",
            "news": [
                {
                    "title": "去过还想去的奥林匹克，酷热又荒凉的死亡谷（多图）",
                    "url": "http://news-at.zhihu.com/api/1.2/news/4517537",
                    "image": "http://pic4.zhimg.com/87324b315fc1674451b56011ed5ead9d.jpg",
                    "share_url": "http://daily.zhihu.com/story/4517537",
                    "thumbnail": "http://pic2.zhimg.com/d4691da85d8f7c4a845bcac5ec49f479.jpg",
                    "ga_prefix": "021019",
                    "id": 4517537
                },
                {
                     # 标题
                     # json 格式，文章内容是 html 的，应该是移动端用的。
                     # 640*640 大图
                     # 网页形式请用这个，直接跳到官方的知乎日报文章
                     # 150*150 小图
                     # Google Analytics 使用
                     # 文章 id， 是 url 和 share_url 链接最后的数字
                }
                ...
            ],
            "is_today": true,   # 是不是今天，只有今天才会有 top_stories, 使用 before/<date> 格式请求得到的则没有 'is_today' 和 'top_stories'
            "top_stories": [    # top_stories 中的新闻就是 news 中的，用于移动端界面顶部 ViewPager 滚动显示的显示内容.
                {
                    "image_source": "Yestone.com 版权图片库",
                    "title": "一群大佬都让我们警惕人工智能，这不是危言耸听",
                    "url": "http://news-at.zhihu.com/api/1.2/news/4517980",
                    "image": "http://pic2.zhimg.com/6d6f508e1bb6ff1f2e39c40423feb4f4.jpg",
                    "share_url": "http://daily.zhihu.com/story/4517980",
                    "ga_prefix": "021007",
                    "id": 4517980
                },
                {
                    ...
                }
            ],
            "display_date": "2015.2.10 星期二"
        }
