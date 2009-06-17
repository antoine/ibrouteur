-- phpMyAdmin SQL Dump
-- version 2.6.4-pl3
-- http://www.phpmyadmin.net
-- 
-- Host: localhost
-- Generation Time: Apr 24, 2006 at 06:57 AM
-- Server version: 5.0.19
-- PHP Version: 5.1.2-1.dotdeb.2
-- 
-- Database: `antoine_images`
-- 

-- --------------------------------------------------------

-- 
-- Table structure for table `images`
-- 

  CREATE TABLE `images` (
      `id` int(11) NOT NULL auto_increment,
      `filename` tinytext NOT NULL,
      `date` date NOT NULL,
      `album` varchar(64) NOT NULL,
      `location` varchar(64) NOT NULL,
      `author` varchar(32) NOT NULL,
      `batch` date NOT NULL,
      `country` varchar(32) NOT NULL,
      PRIMARY KEY  (`id`),
      KEY `date` (`date`),
      KEY `album` (`album`),
      KEY `location` (`location`),
      KEY `country` (`country`),
      KEY `batch` (`batch`)
      ) ENGINE=MyISAM DEFAULT CHARSET=latin1;

  -- --------------------------------------------------------

  -- 
  -- Table structure for table `images_subjects`
  -- 

  CREATE TABLE `images_subjects` (
      `image_id` int(11) NOT NULL,
      `subject_id` int(11) NOT NULL,
      PRIMARY KEY  (`image_id`,`subject_id`)
      ) ENGINE=MyISAM DEFAULT CHARSET=latin1;

  -- --------------------------------------------------------

  -- 
  -- Table structure for table `images_tags`
  -- 

  CREATE TABLE `images_tags` (
      `image_id` int(11) NOT NULL,
      `tag_id` int(11) NOT NULL,
      PRIMARY KEY  (`image_id`,`tag_id`)
      ) ENGINE=MyISAM DEFAULT CHARSET=latin1;

  -- --------------------------------------------------------

  -- 
  -- Table structure for table `subjects`
  -- 

  CREATE TABLE `subjects` (
      `id` int(11) NOT NULL auto_increment,
      `value` varchar(64) NOT NULL,
      PRIMARY KEY  (`id`),
      UNIQUE KEY `value` (`value`)
      ) ENGINE=MyISAM DEFAULT CHARSET=latin1;

  -- --------------------------------------------------------

  -- 
  -- Table structure for table `tags`
  -- 

  CREATE TABLE `tags` (
      `id` int(11) NOT NULL auto_increment,
      `value` varchar(64) NOT NULL,
      PRIMARY KEY  (`id`),
      UNIQUE KEY `value` (`value`)
      ) ENGINE=MyISAM DEFAULT CHARSET=latin1;

