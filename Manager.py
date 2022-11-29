import os
import shutil
import PictureDownloader

def main():
    while True:
        ArtistName = input("請輸入作者名字：")
        ArtistID = int(input("請輸入作者UID："))
        print(f"開始獲取{ArtistName}所有作品")
        if not os.path.isdir(f"IMG\{ArtistName}"):
            os.mkdir(f"IMG\{ArtistName}")
            PictureDownloader.ArtistDownloader(ArtistName,ArtistID)
        else:
            shutil.rmtree(f"IMG\{ArtistName}")
            os.mkdir(f"IMG\{ArtistName}")
            PictureDownloader.ArtistDownloader(ArtistName,ArtistID)
        print(f"獲取{ArtistName}所有作品已完成\n")

if __name__ == "__main__":
    main()