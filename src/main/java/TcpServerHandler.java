import io.netty.buffer.ByteBuf;
import io.netty.buffer.Unpooled;
import io.netty.channel.ChannelFutureListener;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.ChannelInboundHandlerAdapter;
import io.netty.util.CharsetUtil;

import java.io.File;
import java.io.FileOutputStream;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Created by xujiayu on 17/12/28.
 */
public class TcpServerHandler extends ChannelInboundHandlerAdapter {
    private final static char[] HEX_ARRAY = "0123456789ABCDEF".toCharArray();
    private final static String PREFIX = "DCCDAAAAE0";
    private final static String HEARTBEAT = "010101010101010101010101";

    private String path;

    public TcpServerHandler(String path) {
        this.path = path;
    }

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) throws Exception {
        ByteBuf inBuffer = (ByteBuf) msg;
        byte [] bytes = new byte[inBuffer.readableBytes()];
        inBuffer.readBytes(bytes);

        String string = new String(bytes);
        if (string.equals(HEARTBEAT)) {
            System.out.println(HEARTBEAT);
            ctx.write(Unpooled.copiedBuffer(HEARTBEAT, CharsetUtil.UTF_8));
        }
//        String heartbeat = string;
//        if (string.contains(PREFIX)) {
//            heartbeat = string.substring(0, string.indexOf(PREFIX));
//        }
//
//        System.out.println(heartbeat);

        String hexStr = bytesToHex(bytes);
        writeToFile(path, hexStr);

//        ctx.write(Unpooled.copiedBuffer(heartbeat, CharsetUtil.UTF_8));
    }

//    @Override
//    public void channelReadComplete(ChannelHandlerContext ctx) throws Exception {
//        ctx.writeAndFlush(Unpooled.EMPTY_BUFFER)
//                .addListener(ChannelFutureListener.CLOSE);
//    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) throws Exception {
        cause.printStackTrace();
        ctx.close();
    }

    // 写入文件
    public void writeToFile(String path, String hexStr) throws Exception {
//        String time = String.valueOf(System.currentTimeMillis()).substring(0, 10);
        String time = String.valueOf(System.currentTimeMillis());
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd");
        String date = sdf.format(new Date());
//        System.out.println(date);
        String filename = path.concat(File.separator).concat(date);
        File file = new File(filename);
        if (!file.exists()) {
            boolean flag = file.createNewFile();
        }
        FileOutputStream fileOutputStream = new FileOutputStream(file, true);
        String string = hexStr.concat("|").concat(time);
        fileOutputStream.write(string.getBytes());
        fileOutputStream.write(System.getProperty("line.separator").getBytes());
        fileOutputStream.close();
    }

    // 字节数组转十六进制，反序列化
    public static String bytesToHex(byte[] bytes) {
        char[] hexChars = new char[bytes.length * 2];
        for ( int j = 0; j < bytes.length; j++ ) {
            int v = bytes[j] & 0xFF;
            hexChars[j * 2] = HEX_ARRAY[v >>> 4];
            hexChars[j * 2 + 1] = HEX_ARRAY[v & 0x0F];
        }
        return new String(hexChars);
    }
}
