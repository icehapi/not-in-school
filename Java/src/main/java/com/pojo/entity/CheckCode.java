package com.pojo.entity;

import lombok.Data;
import org.springframework.stereotype.Repository;

/**
 * @author hapi
 * @create 2021-08-12 13:02
 **/

@Data
@Repository
public class CheckCode {

    private String uploadCode = "";

    private String updateCode = "";

    public boolean verifyCode(String code, String type) {
        if("upload".equals(type)) {
            return uploadCode.equals(transformCode(code));
        } else if("update".equals(type)) {
            return updateCode.equals(transformCode(code));
        }
        return false;
    }

    private String transformCode(String code) {
        StringBuffer sb = new StringBuffer();
        char ch;

        for(int i = 1;i <= 32;i++) {
            ch = code.charAt(i - 1);
            if(Character.isDigit(ch)) {
                sb.append((char)('0' + (ch - '0' + i) % 10));
            } else if(ch >= 'a' && ch <= 'z') {
                sb.append((char)('a' + (ch - 'a' + i) % 26));
            } else if(ch >= 'A' && ch <= 'Z') {
                sb.append((char)('A' + (ch - 'A' + i) % 26));
            }
        }

        return sb.toString();
    }
}
