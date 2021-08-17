package com.controller;

import com.pojo.entity.CheckCode;
import com.service.UserService;
import com.utils.JsonData;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;


import javax.servlet.http.HttpServletRequest;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.Map;


@RestController
public class UserController {

    @Autowired
    private UserService userService;

    @Autowired
    private CheckCode cc;

    @RequestMapping(value="/user")
    public boolean addUser(HttpServletRequest request) {
        String code = request.getParameter("code");

        if(cc.verifyCode(code, "upload")) {

            String token = request.getParameter("token");
            if("".equals(token) || token == null) {
                return false;
            }

            Map<String, String> userInfo = new HashMap<String, String>();

            userInfo.put("token", token);
            userInfo.put("province", request.getParameter("province"));
            userInfo.put("city", request.getParameter("city"));
            userInfo.put("district", request.getParameter("district"));
            userInfo.put("township", request.getParameter("township"));
            userInfo.put("street", request.getParameter("street"));
            userInfo.put("areacode", request.getParameter("areacode"));
            userInfo.put("lng", request.getParameter("lng"));
            userInfo.put("lat", request.getParameter("lat"));
            userInfo.put("state", request.getParameter("state"));

            System.out.println(userInfo);

            return userService.saveByMap(userInfo);
        }

        return false;
    }
}
