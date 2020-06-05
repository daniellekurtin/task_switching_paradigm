-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 05, 2020 at 10:33 PM
-- Server version: 10.1.40-MariaDB
-- PHP Version: 7.3.5

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Database: `task-switching-game`
--

-- --------------------------------------------------------

--
-- Table structure for table `tspdata`
--

CREATE TABLE `tspdata` (
  `auto_participant_id` varchar(250) DEFAULT NULL,
  `participant_id` varchar(250) DEFAULT NULL,
  `participant_age` varchar(250) DEFAULT NULL,
  `participant_gender` varchar(250) DEFAULT NULL,
  `view_history` varchar(250) DEFAULT NULL,
  `rt` varchar(250) DEFAULT NULL,
  `trial_type` varchar(250) DEFAULT NULL,
  `trial_index` varchar(250) DEFAULT NULL,
  `time_elapsed` varchar(250) DEFAULT NULL,
  `internal_node_id` varchar(250) DEFAULT NULL,
  `blueprint_id` varchar(250) DEFAULT NULL,
  `check_times` varchar(250) DEFAULT NULL,
  `responses` varchar(250) DEFAULT NULL,
  `start_time` varchar(250) DEFAULT NULL,
  `end_time` varchar(250) DEFAULT NULL,
  `stimulus_on` varchar(250) DEFAULT NULL,
  `stimulus_off` varchar(250) DEFAULT NULL,
  `response_enabled_time` varchar(250) DEFAULT NULL,
  `response_time` varchar(250) DEFAULT NULL,
  `response_answer` varchar(250) DEFAULT NULL,
  `answer_index` varchar(250) DEFAULT NULL,
  `response_correct` varchar(250) DEFAULT NULL,
  `trial_task_type` varchar(250) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
COMMIT;
