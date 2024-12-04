-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 04, 2024 at 06:57 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `buy_sell_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `comments`
--

CREATE TABLE `comments` (
  `id` int(11) NOT NULL,
  `post_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `comment_text` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `comments`
--

INSERT INTO `comments` (`id`, `post_id`, `user_id`, `comment_text`, `created_at`) VALUES
(65, 34, 8, 'ok', '2024-12-04 17:55:57'),
(66, 34, 8, 'oksd', '2024-12-04 17:56:01');

-- --------------------------------------------------------

--
-- Table structure for table `posts`
--

CREATE TABLE `posts` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `interest` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `posts`
--

INSERT INTO `posts` (`id`, `user_id`, `image`, `description`, `price`, `created_at`, `interest`) VALUES
(34, 8, 'download.jpeg', 'full and freshhss', 3000.00, '2024-12-04 17:55:16', 0);

-- --------------------------------------------------------

--
-- Table structure for table `post_interests`
--

CREATE TABLE `post_interests` (
  `id` int(11) NOT NULL,
  `post_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `srs_files`
--

CREATE TABLE `srs_files` (
  `id` int(11) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `file_type` varchar(50) NOT NULL,
  `file_content` longblob NOT NULL,
  `uploaded_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `file_path` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `srs_files`
--

INSERT INTO `srs_files` (`id`, `file_name`, `file_type`, `file_content`, `uploaded_at`, `file_path`) VALUES
(7, 'RxResume_1732857302479.pdf', 'application/pdf', '', '2024-12-04 17:53:37', 'static/uploads\\RxResume_1732857302479.pdf');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `is_admin` tinyint(1) DEFAULT 0,
  `profile_pic` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password`, `is_admin`, `profile_pic`) VALUES
(8, 'Shafin Ahmed', 'shafin@gmail.com', '$2b$12$JGkxH6rWC4B1N//tubQz1.o65GwI.tQk.ZPitpauO3GcFF36SSEmW', 0, 'Profile_picture_2.png'),
(9, 'test1', 'test1@gmail.com', '$2b$12$w/iTOLl3SD4LpLzZoo094OFJVQ2b2AOKFk9HOuk8FmvfMRjkm10a6', 0, NULL),
(10, 'test2', 'test2@gmail.com', '$2b$12$RM8xpnjXQbpRfoPgHL1ucuJ03tCD8Xl2wB8q6YuKSwspF4/XTFpRy', 0, 'clipart3467636.png'),
(11, 'admin', 'admin@gmail.com', '$2b$12$z.yzvuhCq1eVCfD9AmPzp.72MV6E.EaeEqhtzmFPG3vHOkboaKJTm', 1, NULL),
(12, 'test1', 'test1@gmail.com', '$2b$12$8knotjLjdtmR5wZW8WNlseoJvXV6ofsd0BkV7XttPPE40S8z11MpO', 0, NULL),
(13, 'test1', 'test1@gmail.com', '$2b$12$HjXG7kqxV8g/33lMyYmcG.4go0HOOX3VY5uH4h4/hqqdl.We9oXFW', 0, NULL),
(14, 'test3', 'test3@gmail.com', '$2b$12$DGRcWmhqV5pceHLLF4iZN.LoCojNXMiM3wdz8aqODkzg9FEqifPZG', 0, NULL),
(15, 'Zohir', 'zohir@gmail.com', '$2b$12$SR87CxPW2/fs65jrEVGYkO0O/apbRRFOTMJr9rSeh75eoROEqLXmO', 0, NULL),
(16, 'Boni Amin', 'boni@gmail.com', '$2b$12$a4SnIxvnonX1FQGfJqxM..QCqvIXqYqCDeUboKp5gMol6k4sBLTgS', 0, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `comments`
--
ALTER TABLE `comments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `post_id` (`post_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `post_interests`
--
ALTER TABLE `post_interests`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `post_id` (`post_id`,`user_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `srs_files`
--
ALTER TABLE `srs_files`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `comments`
--
ALTER TABLE `comments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=67;

--
-- AUTO_INCREMENT for table `posts`
--
ALTER TABLE `posts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT for table `post_interests`
--
ALTER TABLE `post_interests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `srs_files`
--
ALTER TABLE `srs_files`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `comments`
--
ALTER TABLE `comments`
  ADD CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`),
  ADD CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `posts`
--
ALTER TABLE `posts`
  ADD CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `post_interests`
--
ALTER TABLE `post_interests`
  ADD CONSTRAINT `post_interests_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`),
  ADD CONSTRAINT `post_interests_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
