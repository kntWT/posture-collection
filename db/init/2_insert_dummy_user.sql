SET CHARSET UTF8;
CREATE DATABASE IF NOT EXISTS `posture_correction_db` DEFAULT CHARACTER SET utf8  /*!80016 DEFAULT ENCRYPTION='N' */;

USE `posture_correction_db`;

INSERT INTO `users` (`name`, `password`) VALUES ("anonymous", "posture-correction");