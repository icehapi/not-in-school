package com.pojo.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import lombok.Data;

import javax.persistence.Entity;


@Data
public class User {

    @TableId(type = IdType.INPUT)
    private String token;

    private String province;

    private String city;

    private String district;

    private String township;

    private String street;

    private String areacode;

    private String lng;

    private String lat;

    private String state;

}
