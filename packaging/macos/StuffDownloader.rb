cask "stuff-downloader" do
  version "1.2.0"
  if Hardware::CPU.intel?
    sha256 :no_check # TODO: Replace with the actual intel DMG sha256 once built
    url "https://github.com/AlokaWarnakula/stuff-downloader/releases/download/v#{version}/StuffDownloader-#{version}-macos-x86_64.dmg"
  else
    sha256 "a16d573d2ac3db247438b257deb13577e72652e23ccf1467ca040db6cd0fa7f8"
    url "https://github.com/AlokaWarnakula/stuff-downloader/releases/download/v#{version}/StuffDownloader-#{version}-macos-arm64.dmg"
  end

  name "Stuff Downloader"
  desc "Desktop app for downloading videos, music and image galleries"
  homepage "https://github.com/AlokaWarnakula/stuff-downloader"

  app "StuffDownloader.app"

  zap trash: [
    "~/Library/Application Support/StuffDownloader",
  ]
end
