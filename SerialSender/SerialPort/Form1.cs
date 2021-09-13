using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.IO.Ports;
using System.Linq;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace SerialPort
{
    public partial class Form1 : Form
    {

        System.Diagnostics.Process p = new System.Diagnostics.Process();

        String serialPortName;
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            string[] ports = System.IO.Ports.SerialPort.GetPortNames();//获取电脑上可用串口号
            comboBox1.Items.AddRange(ports);//给comboBox1添加数据
            comboBox1.SelectedIndex = comboBox1.Items.Count > 0 ? 0 : -1;//如果里面有数据,显示第0个

            comboBox2.Text = "115200";/*默认波特率:115200*/
            comboBox3.Text = "1";/*默认停止位:1*/
            comboBox4.Text = "8";/*默认数据位:8*/
            comboBox5.Text = "无";/*默认奇偶校验位:无*/
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (button1.Text == "打开串口"){//如果按钮显示的是打开
                try{//防止意外错误
                    serialPort1.PortName = comboBox1.Text;//获取comboBox1要打开的串口号
                    serialPortName = comboBox1.Text;
                    serialPort1.BaudRate = int.Parse(comboBox2.Text);//获取comboBox2选择的波特率
                    serialPort1.DataBits = int.Parse(comboBox4.Text);//设置数据位
                    /*设置停止位*/
                    if (comboBox3.Text == "1") { serialPort1.StopBits = StopBits.One; }
                    else if (comboBox3.Text == "1.5") { serialPort1.StopBits = StopBits.OnePointFive; }
                    else if (comboBox3.Text == "2") { serialPort1.StopBits = StopBits.Two; }
                    /*设置奇偶校验*/
                    if (comboBox5.Text == "无") { serialPort1.Parity = Parity.None; }
                    else if (comboBox5.Text == "奇校验") { serialPort1.Parity = Parity.Odd; }
                    else if (comboBox5.Text == "偶校验") { serialPort1.Parity = Parity.Even; }

                    serialPort1.Open();//打开串口
                    button1.Text = "关闭串口";//按钮显示关闭串口
                }
                catch (Exception err)
                {
                    MessageBox.Show("打开失败"+ err.ToString(), "提示!");//对话框显示打开失败
                }
            }
            else{//要关闭串口
                try{//防止意外错误
                    serialPort1.Close();//关闭串口
                }
                catch (Exception){}
                button1.Text = "打开串口";//按钮显示打开
            }
        }


        protected override void WndProc(ref Message m)
        {
            if (m.Msg == 0x0219){//设备改变
                if (m.WParam.ToInt32() == 0x8004){//usb串口拔出
                    string[] ports = System.IO.Ports.SerialPort.GetPortNames();//重新获取串口
                    comboBox1.Items.Clear();//清除comboBox里面的数据
                    comboBox1.Items.AddRange(ports);//给comboBox1添加数据
                    if (button1.Text == "关闭串口"){//用户打开过串口
                        if (!serialPort1.IsOpen){//用户打开的串口被关闭:说明热插拔是用户打开的串口
                            button1.Text = "打开串口";
                            serialPort1.Dispose();//释放掉原先的串口资源
                            comboBox1.SelectedIndex = comboBox1.Items.Count > 0 ? 0 : -1;//显示获取的第一个串口号
                        }
                        else{
                            comboBox1.Text = serialPortName;//显示用户打开的那个串口号
                        }
                    }
                    else{//用户没有打开过串口
                        comboBox1.SelectedIndex = comboBox1.Items.Count > 0 ? 0 : -1;//显示获取的第一个串口号
                    }
                }
                else if (m.WParam.ToInt32() == 0x8000){//usb串口连接上
                    string[] ports = System.IO.Ports.SerialPort.GetPortNames();//重新获取串口
                    comboBox1.Items.Clear();
                    comboBox1.Items.AddRange(ports);
                    if (button1.Text == "关闭串口"){//用户打开过一个串口
                        comboBox1.Text = serialPortName;//显示用户打开的那个串口号
                    }
                    else{
                        comboBox1.SelectedIndex = comboBox1.Items.Count > 0 ? 0 : -1;//显示获取的第一个串口号
                    }
                }
            }
            base.WndProc(ref m);
        }

        private void serialPort1_DataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            int len = serialPort1.BytesToRead;//获取可以读取的字节数
            byte[] buff = new byte[len];//创建缓存数据数组
            serialPort1.Read(buff, 0, len);//把数据读取到buff数组
            
            Invoke((new Action(() =>{//C# 3.0以后代替委托的新方法
                if (checkBox1.Checked){//16进制显示
                    textBox1.AppendText(byteToHexStr(buff));
                }
                else{
                    textBox1.AppendText(Encoding.Default.GetString(buff));//对话框追加显示数据
                }
            })));
        }

        /// <字节数组转16进制字符串>
        /// <param name="bytes"></param>
        /// <returns> String 16进制显示形式</returns>
        public static string byteToHexStr(byte[] bytes)
        {
            string returnStr = "";
            try{
                if (bytes != null){
                    for (int i = 0; i < bytes.Length; i++){
                        returnStr += bytes[i].ToString("X2");
                        returnStr += " ";//两个16进制用空格隔开,方便看数据
                    }
                }
                return returnStr;
            }
            catch (Exception){
                return returnStr;
            }
        }




        private void button2_Click(object sender, EventArgs e)
        {
            textBox1.Clear();//清除接收对话框显示的数据
        }



        private void button3_Click(object sender, EventArgs e)
        {
            String Str = textBox2.Text.ToString();//获取发送文本框里面的数据
            try
            {
                if (Str.Length > 0)
                {
                    if (checkBox2.Checked)//16进制发送
                    {
                        byte[] byt = strToToHexByte(Str);
                        serialPort1.Write(byt, 0, byt.Length);
                    }
                    else
                    {
                        serialPort1.Write(Str);//串口发送数据
                    }
                }
            }
            catch (Exception){ }
        }


        /// <字符串转16进制格式-不够自动前面补零>
        /// 
        /// </summary>
        /// <param name="hexString"></param>
        /// <returns></returns>
        private static byte[] strToToHexByte(String hexString)
        {
            int i;
            hexString = hexString.Replace(" ", "");//清除空格
            if ((hexString.Length % 2) != 0)//奇数个
            {
                byte[] returnBytes = new byte[(hexString.Length + 1) / 2];
                try
                {
                    for (i = 0; i < (hexString.Length - 1) / 2; i++)
                    {
                        returnBytes[i] = Convert.ToByte(hexString.Substring(i * 2, 2), 16);
                    }
                    returnBytes[returnBytes.Length - 1] = Convert.ToByte(hexString.Substring(hexString.Length - 1, 1).PadLeft(2, '0'), 16);
                }
                catch
                {
                    MessageBox.Show("含有非16进制字符", "提示");
                    return null;
                }
                return returnBytes;
            }
            else
            {
                byte[] returnBytes = new byte[(hexString.Length) / 2];
                try
                {
                    for (i = 0; i < returnBytes.Length; i++)
                    {
                        returnBytes[i] = Convert.ToByte(hexString.Substring(i * 2, 2), 16);
                    }
                }
                catch
                {
                    MessageBox.Show("含有非16进制字符", "提示");
                    return null;
                }
                return returnBytes;
            }
        }

        private void button4_Click(object sender, EventArgs e)
        {
            textBox2.Clear();//清除发送文本框里面的内容
        }
        public void log(string str)
        {
            Invoke(new Action(() =>
            {
                textBox3.AppendText(str);
            }));
        }
        public void start()
        {
            p.StartInfo = new System.Diagnostics.ProcessStartInfo();
            p.StartInfo.WorkingDirectory = "E:/Python/Genshin-SmartFishingRod-master/dist/main";
            p.StartInfo.FileName = "E:/Python/Genshin-SmartFishingRod-master/dist/main.exe";
            p.StartInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
            p.StartInfo.RedirectStandardOutput = true;
            p.StartInfo.RedirectStandardError = true;
            p.StartInfo.UseShellExecute = false;
            //p.StartInfo.CreateNoWindow = true;//让窗体不显示
            p.Start();
            StreamReader reader = p.StandardOutput;//截取输出流
            while (!reader.EndOfStream)
            {
                string line = reader.ReadLine();//每次读取一行

                log(line + Environment.NewLine);
                if (line=="1"||line=="0")
                {
                    serialPort1.Write(line);
                }
            }
            p.WaitForExit();//等待程序执行完退出进程
            p.Close();
        }
        private void button5_Click(object sender, EventArgs e)
        {
            Thread thread = new Thread(new ThreadStart(start));//创建线程
            thread.Start();
        }


        private void Form1_FormClosed(object sender, FormClosedEventArgs e)
        {
            System.Environment.Exit(0);
        }
    }
}
