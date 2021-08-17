package com.service;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.mapper.UserMapper;
import com.pojo.entity.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class UserService extends ServiceImpl<UserMapper, User> {

    @Autowired
    private UserMapper userMapper;

    /**
     * @param userInfo
     * @return
     */
    public boolean saveByMap(Map<String, String> userInfo) {
        User user = parseToUser(userInfo);

        if (user != null) {
            return saveOrUpdate(user);
        } else {
            return false;
        }

    }

    private User parseToUser(Map<String, String> userInfo) {
        if (userInfo.containsKey("token") && userInfo.containsKey("state")) {
            User user = new User();
            user.setToken(userInfo.get("token"));
            user.setState(userInfo.get("state"));
            if ("1".equals(userInfo.get("state"))) {
                if (userInfo.containsKey("province") && userInfo.containsKey("city") && userInfo.containsKey("district") && userInfo.containsKey("township")
                        && userInfo.containsKey("street") && userInfo.containsKey("areacode") && userInfo.containsKey("lng") && userInfo.containsKey("lat")) {
                    user.setProvince(userInfo.get("province"));
                    user.setCity(userInfo.get("city"));
                    user.setDistrict(userInfo.get("district"));
                    user.setTownship(userInfo.get("township"));
                    user.setStreet(userInfo.get("street"));
                    user.setAreacode(userInfo.get("areacode"));
                    user.setLng(userInfo.get("lng"));
                    user.setLat(userInfo.get("lat"));
                } else {
                    return null;
                }
            }
            return user;
        }
        return null;
    }
}

