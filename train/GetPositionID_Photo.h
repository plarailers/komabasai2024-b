/* 
	Photo-Refrector to ESP32 Connections
	===========

	=======
	2023-05-07
*/


class GetPositionID_Photo
{
	private:
		int 	positionID;
    public:
		GetPositionID_Photo();
        void    photoSetup();
        int     getPositionID();
};

GetPositionID_Photo::GetPositionID_Photo() {
	this->positionID = 0;
}

void GetPositionID_Photo::photoSetup() {

}

int GetPositionID_Photo::getPositionID() {
    return positionID;
}