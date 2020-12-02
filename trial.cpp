#include<ros/ros.h>
#include<cv_bridge/cv_bridge.h>
#include<opencv2/highgui/highgui.hpp>
#include<iostream>

using namespace std;
using namespace cv;

class cam_test
{
	public:
		cam_test(){
			VideoCapture cap(CV_CAP_ANY);
			if (!cap.isOpened())
			{
				cout<<"Cannot Open The Video Camera"<<endl;
			}
			double dWidth = cap.get(CV_CAP_PROP_FRAME_WIDTH);
			double dHeight = cap.get(CV_CAP_PROP_FRAME_HEIGHT);

			cout<<"Frame Size: "<< dWidth <<"x" <<dHeight<<endl;

			cvNamedWindow("MyVideo", CV_WINDOW_AUTOSIZE);

			while(1)
			{
				Mat frame;
				bool bSuccess = cap.read(frame);

				if (!bSuccess)
				{
					cout<< "Cannot get a frame from the video stream"<<endl;
					break;
				}
				imshow("MyVideo",frame);

				if(waitKey(30) == 27)
				{
					cout<<"Escape key pressed by the user!"<<endl;
					break;
				}

			}
		}
		
		~cam_test(){
			cvDestroyWindow("Camera_Output");
		}
};

int main (int argc,char **argv)
{
	ros::init(argc, argv, "trial1");
	cam_test cam_object;
}
