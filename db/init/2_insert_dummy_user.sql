SET CHARSET UTF8;
CREATE DATABASE IF NOT EXISTS `posture_collection_db` DEFAULT CHARACTER SET utf8  /*!80016 DEFAULT ENCRYPTION='N' */;

USE `posture_collection_db`;

INSERT INTO `users` (`name`, `password`) VALUES ("anonymous", "posture-collection");