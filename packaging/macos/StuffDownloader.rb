cask "stuff-downloader" do
  version "1.2.0"
  sha256 "a16d573d2ac3db247438b257deb13577e72652e23ccf1467ca040db6cd0fa7f8"

  url "https://github.com/AlokaWarnakula/stuff-downloader/releases/download/v#{version}/StuffDownloader-#{version}-macos-arm64.dmg"

  name "Stuff Downloader"
  desc "Desktop app for downloading videos, music and image galleries"
  homepage "https://github.com/AlokaWarnakula/stuff-downloader"

  app "StuffDownloader.app"

  zap trash: [
    "~/Library/Application Support/StuffDownloader",
  ]
end
