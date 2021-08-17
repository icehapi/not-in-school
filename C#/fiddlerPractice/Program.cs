using System;
using System.Net;
using System.Security.Cryptography.X509Certificates;
using System.Threading;
using Fiddler;
using Newtonsoft.Json;
using System.Runtime.InteropServices;
using System.Device.Location;
using System.IO;
using Newtonsoft.Json.Linq;
using System.Net.Http;
using System.Windows;
using System.Text;
using System.Web.UI.WebControls;
using System.Xml.Linq;
using System.Text.RegularExpressions;
using System.Diagnostics;
using System.Net.NetworkInformation;

namespace Demo
{
    class Program
    {
        // 服务器IP
        const string serverIP = "";
        // 本地测试
        //const string serverIP = "localhost.charlesproxy.com";
        // 高德地图ApiKey
        const string gaodeKey = "";
        // 腾讯地图ApiKey
        // const string tengxunKey = "";
        // 腾讯地图签名
        // const string tengxunsig = "";
        // 上传识别码
        const string uploadCode = "";
        // 在线更新识别码
        const string updateCode = "";

        public delegate bool ControlCtrlDelegate(int CtrlType);
        [DllImport("kernel32.dll")]
        private static extern bool SetConsoleCtrlHandler(ControlCtrlDelegate HandlerRoutine, bool Add);
        private static ControlCtrlDelegate cancelHandler = new ControlCtrlDelegate(HandlerRoutine);

        class Locate
        {
            /// <summary>
            /// 获取地理位置
            /// </summary>
            /// <param name="addr"></param>
            /// <param name="loca"></param>
            /// <returns></returns>
            public static bool getLocation(string[] addr, string[] loca)
            {
                try
                {
                    string txUrl = "https://apis.map.qq.com/ws/location/v1/ip?key=RPEBZ-J2ZWW-2CIRC-OO3Q2-HH7X2-7GBEJ&sig=7817334a06d1ddb3bac9137847e65b6b";
                    string addrUrl = "https://restapi.amap.com/v3/geocode/regeo?" + "key=" + gaodeKey + "&radius=0" + "&location=";
                    Txlocation txaddr = JsonConvert.DeserializeObject<Txlocation>(getInfomation(txUrl));
                    if (txaddr != null && Convert.ToInt32(txaddr.status) == 0)
                    {
                        loca[0] = txaddr.result.location.lng;
                        loca[1] = txaddr.result.location.lat;
                        addr[0] = txaddr.result.ad_info.province;
                        addr[1] = txaddr.result.ad_info.city;
                        string lnglat = loca[0] + "," + loca[1];
                        addrUrl += lnglat;
                        gaode_regeocode addrInfo = JsonConvert.DeserializeObject<gaode_regeocode>(getInfomation(addrUrl));
                        if (Convert.ToInt32(addrInfo.status) == 1)
                        {
                            addr[2] = addrInfo.regeocode.addressComponent.district;
                            addr[3] = addrInfo.regeocode.addressComponent.township;
                            addr[4] = addrInfo.regeocode.addressComponent.streetNumber.street;
                            addr[5] = addrInfo.regeocode.addressComponent.adcode;
                        }
                        else
                        {
                            MessageBox.Show("缺少部分定位信息，建议重新定位");
                        }
                    }
                    else
                    {
                        string gaodeUrl = "https://restapi.amap.com/v5/ip?type=4" + "&ip=" + getIP() + "&key=" + gaodeKey;
                        Gaodelocation gdaddr = JsonConvert.DeserializeObject<Gaodelocation>(getInfomation(gaodeUrl));
                        if (gdaddr != null && Convert.ToInt32(gdaddr.status) == 1)
                        {
                            string[] temp = gdaddr.location.Split(',');
                            loca[0] = temp[0];
                            loca[1] = temp[1];
                            addr[0] = gdaddr.province;
                            addr[1] = gdaddr.city;
                            addr[2] = gdaddr.district;

                            string lnglat = loca[0] + "," + loca[1];
                            addrUrl += lnglat;
                            gaode_regeocode addrInfo = JsonConvert.DeserializeObject<gaode_regeocode>(getInfomation(addrUrl));
                            if(Convert.ToInt32(addrInfo.status) == 1)
                            {
                                addr[3] = addrInfo.regeocode.addressComponent.township;
                                addr[4] = addrInfo.regeocode.addressComponent.streetNumber.street;
                                addr[5] = addrInfo.regeocode.addressComponent.adcode;
                            }
                            else
                            {
                                MessageBox.Show("缺少部分定位信息，建议重新定位");
                            }
                        }
                        else
                        {
                            throw new System.NullReferenceException();
                        }
                    }
                    return true;
                }
                catch (Exception e)
                {
                    MessageBox.Show("定位失败，出现异常");
                    return false;
                }
            }

            /// <summary>
            /// 调用地图api方法
            /// </summary>
            /// <param name="url"></param>
            /// <returns></returns>
            public static string getInfomation(string url)
            {
                try
                {
                    ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12 | SecurityProtocolType.Tls11;
                    HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);
                    request.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.25 Safari/537.36 Edg/93.0.961.18";
                    request.Headers.Add("Accept-Encoding", "gzip, deflate, br");
                    request.Referer = "https://servicewechat.com/wxce6d08f781975d91/179/page-frame.html";
                    HttpWebResponse response = (HttpWebResponse)request.GetResponse();
                    System.IO.Stream responseStream = response.GetResponseStream();
                    System.IO.StreamReader sr = new System.IO.StreamReader(responseStream, System.Text.Encoding.GetEncoding("utf-8"));
                    string responseText = sr.ReadToEnd();
                    sr.Close();
                    sr.Dispose();
                    responseStream.Close();
                    string jsonData = responseText;
                    return jsonData;
                }
                catch (Exception e)
                {
                    MessageBox.Show("定位失败，出现异常");
                    return null;
                }
            }

            /// <summary>
            /// 发起请求获得ip地址
            /// </summary>
            /// <param name="url"></param>
            /// <param name="encoding"></param>
            /// <returns></returns>
            public static string HttpGetPageHtml(string url, string encoding)
            {
                string pageHtml = string.Empty;
                try
                {
                    using (WebClient MyWebClient = new WebClient())
                    {
                        Encoding encode = Encoding.GetEncoding(encoding);
                        MyWebClient.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36");
                        MyWebClient.Credentials = CredentialCache.DefaultCredentials;//获取或设置用于向Internet资源的请求进行身份验证的网络凭据
                        Byte[] pageData = MyWebClient.DownloadData(url); //从指定网站下载数据
                        pageHtml = encode.GetString(pageData);
                    }
                }
                catch (Exception e)
                {
                    Console.WriteLine("IP获取异常");
                }
                return pageHtml;
            }

            /// <summary>
            /// 从html中通过正则找到ip信息(只支持ipv4地址)
            /// </summary>
            /// <param name="pageHtml"></param>
            /// <returns></returns>
            public static string GetIPFromHtml(String pageHtml)
            {
                //验证ipv4地址
                string reg = @"(?:(?:(25[0-5])|(2[0-4]\d)|((1\d{2})|([1-9]?\d)))\.){3}(?:(25[0-5])|(2[0-4]\d)|((1\d{2})|([1-9]?\d)))";
                string ip = "";
                Match m = Regex.Match(pageHtml, reg);
                if (m.Success)
                {
                    ip = m.Value;
                }
                return ip;
            }

            public static string getIP()
            {
                var html = HttpGetPageHtml("http://www.net.cn/static/customercare/yourip.asp", "gbk");
                return GetIPFromHtml(html);
            }
        }

        public static bool HandlerRoutine(int CtrlType)
        {
            switch (CtrlType)
            {
                case 0:
                    FiddlerApplication.Shutdown(); //Ctrl+C关闭  
                    break;
                case 2:
                    FiddlerApplication.Shutdown(); //按控制台关闭按钮关闭  
                    break;
            }
            Console.ReadLine();
            return false;
        }

        static void Main(string[] args)
        {
            
            Console.WriteLine("正在获取地理位置... \n");
            Console.WriteLine("1.定位(自动获得PC所在位置) 2.学校 3.使用之前提供的地理信息 4.退出程序");
            Console.WriteLine("请输入上述参数:");
            string[] addr = new string[6];
            string[] loca = new string[2];
            string state = "1";
            //Console.WriteLine(GetIP());
            string b =  Console.ReadLine();
            if (b == "1") 
            {
                bool res = Locate.getLocation(addr, loca);
                if(res)
                {
                    Console.WriteLine(addr[0] + " " + addr[1] + " " + addr[2] + " " + addr[3] + " " + addr[4] + " " + addr[5] + " " + loca[0] + " " + loca[1]);
                }
                else
                {
                    Console.WriteLine("地理位置异常，程序即将在2s后退出");
                    Thread.Sleep(2000);
                    Environment.Exit(0);
                }
            } 
            else if (b == "2")
            {
                // 省份
                addr[0] = "";
                // 城市
                addr[1] = "";
                // 地区
                addr[2] = "";
                // 街道
                addr[3] = "";
                // 道路
                addr[4] = "";
                // 地区编码
                addr[5] = "";
                // 经度
                loca[0] = "";
                // 纬度
                loca[1] = "";
                Console.WriteLine(addr[0] + " " + addr[1] + " " + addr[2] + " " + addr[3] + " " + addr[4] + " " + addr[5] + " " + loca[0] + " " + loca[1]);
            } 
            else if(b == "3")
            {
                state = "0";
            }
            else
            {
                Environment.Exit(0);
            }
            if(state == "1")
            {
                Console.WriteLine("\n请确认信息无误，有误信息造成的后果自责。 \n");
            }
            else
            {
                Console.WriteLine("\n请确认之前有上传过地理信息。 \n");
            }
            
            //Thread.Sleep(500);

            SetConsoleCtrlHandler(cancelHandler, true);
            //-----------处理证书-----------
            // 伪造的证书
            X509Certificate2 oRootCert;
            // 如果没有伪造过证书并把伪造的证书加入本机证书库中
            if (null == CertMaker.GetRootCertificate())
            {
                // 创建伪造证书
                CertMaker.createRootCert();

                // 重新获取
                oRootCert = CertMaker.GetRootCertificate();

                // 打开本地证书库
                X509Store certStore = new X509Store(StoreName.Root, StoreLocation.LocalMachine);
                certStore.Open(OpenFlags.ReadWrite);
                try
                {
                    //将伪造的证书加入到本地的证书库
                    certStore.Add(oRootCert);
                }
                finally
                {
                    certStore.Close();
                }
            }
            else
            {
                // 以前伪造过证书，并且本地证书库中保存过伪造的证书
                oRootCert = CertMaker.GetRootCertificate();
            }


            // 指定伪造证书
            FiddlerApplication.oDefaultClientCertificate = oRootCert;
            // 忽略服务器证书错误
            CONFIG.IgnoreServerCertErrors = true;
            // 信任证书
            CertMaker.trustRootCert();
            FiddlerApplication.Prefs.SetBoolPref("fiddler.network.streaming.abortifclientaborts", true);
            // 抓包
            FiddlerApplication.AfterSessionComplete += session => getIDToken(session, addr, loca, state);
            FiddlerApplication.Startup(8001, FiddlerCoreStartupFlags.DecryptSSL | FiddlerCoreStartupFlags.AllowRemoteClients | FiddlerCoreStartupFlags.Default);
            Console.Write("开始捕获token，请打开小程序日检日报页面获取token\n");
            Console.ReadLine();

            // Shutdown:
            FiddlerApplication.Shutdown();
        }

        private static void getIDToken(Session session, string[] addr, string[] loca, string state)
        {
            String a = "getTodayHeatList.json";
            if (session.fullUrl.IndexOf(a) >= 0)
            {
                try
                {
                    String token = session.RequestHeaders.AllValues("jwsession");
                    Console.WriteLine(token);
                    String url = "http://" + serverIP + ":8080/user";

                    HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);

                    string postData = "code=" + uploadCode + "&token=" + token
                            + "&province=" + addr[0] + "&city=" + addr[1] + "&district=" + addr[2] + "&township=" + addr[3]
                            + "&street=" + addr[4] + "&areacode=" + addr[5] + "&lng=" + loca[0] + "&lat=" + loca[1] + "&state=" + state;
                    request.Method = "POST";
                    request.ContentType = "application/x-www-form-urlencoded;charset=UTF-8";
                    byte[] data = Encoding.UTF8.GetBytes(postData);
                    request.ContentLength = data.Length;
                    request.GetRequestStream().Write(data, 0, data.Length);

                    HttpWebResponse response = (HttpWebResponse)request.GetResponse();
                    Stream myResponseStream = response.GetResponseStream();
                    StreamReader myStreamReader = new StreamReader(myResponseStream, Encoding.UTF8);
                    string retString = myStreamReader.ReadToEnd();

                    if (retString == "true")
                    {
                        MessageBox.Show("上传Token成功！！！关闭此窗口后2s程序自动退出，未自动退出请按回车或者Ctrl+C");

                    } 
                    else if(retString == "false")
                    {
                        MessageBox.Show("上传Token失败，关闭此窗口后2s程序自动退出，未自动退出请按回车或者Ctrl+C");
                    }
                }
                catch (Exception e)
                {
                    MessageBox.Show("上传Token异常，关闭此窗口后2s程序自动退出，未自动退出请按回车或者Ctrl+C");
                }
                finally
                {
                    FiddlerApplication.Shutdown();
                    Thread.Sleep(2000);
                    Process.GetCurrentProcess().Kill();
                }
            }
        }

        [Serializable]
        public class gaode_regeocode
        {
            public string status { get; set; }
            public Regeocode regeocode { get; set; }

            [Serializable]
            public class Regeocode
            {
                public AddressComponent addressComponent { get; set; }
            }

            [Serializable]
            public class AddressComponent
            {
                public string province { get; set; }
                public string city { get; set; }
                public string district { get; set; }
                public StreetNumber streetNumber { get; set; }
                public string township { get; set; }
                public string adcode { get; set; }

                public class StreetNumber
                {
                    public string street { get; set; }
                }
            }
        }
        [Serializable]
        public class Gaodelocation
        {
            public string status { get; set; }
            public string province { get; set; }
            public string city { get; set; }
            public string district { get; set; }
            public string location { get; set; }
        }

        public class Txlocation
        {
            public string status { get; set; }
            public Result result { get; set; }

            [Serializable]
            public class Result
            {
                public Location location { get; set; }
                public Ad_Info ad_info { get; set; }

                [Serializable]
                public class Location
                {
                    public string lng { get; set; }
                    public string lat { get; set; }
                }

                [Serializable]
                public class Ad_Info
                {
                    public string province { get; set; }
                    public string city { get; set; }
                    public string district { get; set; }
                    public string adcode { get; set; }
                }
            }
        }
    }
}